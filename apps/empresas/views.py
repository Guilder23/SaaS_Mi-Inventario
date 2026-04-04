from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import Empresa, PagoEmpresa, PagoQRConfig
from apps.usuarios.models import PerfilUsuario
from apps.notificaciones.utils import crear_notificacion


@login_required
def pagos_empresa(request):
    if request.user.is_superuser:
        return redirect("pagos_admin")

    empresa = getattr(request, "empresa", None)
    if not empresa:
        messages.error(request, "No tienes una empresa asignada.")
        return redirect("index")

    if request.method == "POST":
        monto = request.POST.get("monto", "").strip()
        moneda = request.POST.get("moneda", "BOB").strip() or "BOB"
        comprobante = request.FILES.get("comprobante")
        comentario = request.POST.get("comentario", "").strip()

        if not monto or not comprobante:
            messages.error(request, "Monto y comprobante son obligatorios.")
            return redirect("pagos_empresa")

        pago_creado = PagoEmpresa.objects.create(
            empresa=empresa,
            monto=monto,
            moneda=moneda,
            comprobante=comprobante,
            comentario=comentario,
            enviado_por=request.user,
        )

        # Notificar a superusuarios: nuevo comprobante enviado por un administrador
        try:
            url_admin = reverse("pagos_admin")
        except Exception:
            url_admin = None

        superusuarios = User.objects.filter(is_superuser=True).distinct()
        titulo = "Nuevo comprobante de pago"
        mensaje = (
            f"{empresa.nombre}: {pago_creado.monto} {pago_creado.moneda} "
            f"(enviado por {request.user.username})."
        )
        for su in superusuarios:
            crear_notificacion(
                su,
                "pago_pendiente",
                titulo,
                mensaje,
                url=url_admin,
                empresa=empresa,
            )

        messages.success(request, "Comprobante enviado. Espera la aprobacion del super admin.")
        return redirect("pagos_empresa")

    qr_config = PagoQRConfig.objects.filter(activo=True).order_by("-fecha_creacion").first()
    pagos = PagoEmpresa.objects.filter(empresa=empresa).order_by("-fecha_envio")

    hoy = timezone.now().date()
    fecha_vencimiento = empresa.fecha_vencimiento
    dias_restantes = None
    estado_licencia = "sin_pago"
    if fecha_vencimiento:
        dias_restantes = (fecha_vencimiento - hoy).days
        estado_licencia = "vigente" if dias_restantes >= 0 else "vencida"

    # Reglas de UI:
    # - Mostrar QR si NO está pagado (sin_pago o vencida) o si faltan 5 días o menos.
    # - Color amarillo si faltan 5..3 días; rojo si faltan 2 o menos (incluye vencida/sin pago).
    mostrar_qr = (estado_licencia != "vigente") or (dias_restantes is not None and dias_restantes <= 5)

    alerta_licencia = "ok"
    if estado_licencia != "vigente":
        alerta_licencia = "danger"
    elif dias_restantes is not None and dias_restantes <= 2:
        alerta_licencia = "danger"
    elif dias_restantes is not None and dias_restantes <= 5:
        alerta_licencia = "warning"

    context = {
        "empresa": empresa,
        "qr_config": qr_config,
        "pagos": pagos,
        "fecha_vencimiento": fecha_vencimiento,
        "dias_restantes": dias_restantes,
        "estado_licencia": estado_licencia,
        "mostrar_qr": mostrar_qr,
        "alerta_licencia": alerta_licencia,
    }
    return render(request, "empresas/pagos_cliente/pagos_cliente.html", context)


@user_passes_test(lambda user: user.is_superuser)
def pagos_admin(request):
    if request.method == "POST":
        action = request.POST.get("action")
        pago_id = request.POST.get("pago_id")
        pago = get_object_or_404(PagoEmpresa, id=pago_id)

        try:
            url_cliente = reverse("pagos_empresa")
        except Exception:
            url_cliente = None

        def _destinatarios_admin_empresa(pago_obj):
            # Preferir al usuario que envió el comprobante
            if pago_obj.enviado_por:
                return [pago_obj.enviado_por]
            # Fallback: todos los administradores activos de la empresa
            admin_ids = (
                PerfilUsuario.objects.filter(empresa=pago_obj.empresa, rol="administrador", activo=True)
                .exclude(usuario__isnull=True)
                .values_list("usuario_id", flat=True)
            )
            return list(User.objects.filter(id__in=admin_ids))

        if action == "aprobar_pago":
            pago.estado = "aprobado"
            pago.revisado_por = request.user
            pago.fecha_revision = timezone.now()
            pago.save()

            for dest in _destinatarios_admin_empresa(pago):
                crear_notificacion(
                    dest,
                    "pago_aprobado",
                    "Pago aprobado",
                    f"Tu pago de {pago.monto} {pago.moneda} para {pago.empresa.nombre} fue aprobado.",
                    url=url_cliente,
                    empresa=pago.empresa,
                )
            messages.success(request, "Pago aprobado correctamente.")
        elif action == "rechazar_pago":
            pago.estado = "rechazado"
            pago.revisado_por = request.user
            pago.fecha_revision = timezone.now()
            pago.save()

            for dest in _destinatarios_admin_empresa(pago):
                crear_notificacion(
                    dest,
                    "pago_rechazado",
                    "Pago rechazado",
                    f"Tu pago de {pago.monto} {pago.moneda} para {pago.empresa.nombre} fue rechazado.",
                    url=url_cliente,
                    empresa=pago.empresa,
                )
            messages.warning(request, "Pago rechazado.")

        return redirect("pagos_admin")

    pagos_pendientes = PagoEmpresa.objects.filter(estado="pendiente").order_by("-fecha_envio")
    pagos_recientes = PagoEmpresa.objects.exclude(estado="pendiente").order_by("-fecha_envio")[:50]

    context = {
        "pagos_pendientes": pagos_pendientes,
        "pagos_recientes": pagos_recientes,
    }
    return render(request, "empresas/pagos/pagos.html", context)


@user_passes_test(lambda user: user.is_superuser)
def empresas_list(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "crear_empresa":
            nombre = request.POST.get("nombre", "").strip()
            plan = request.POST.get("plan", "basico").strip() or "basico"
            activa = request.POST.get("activa") == "on"
            notas = request.POST.get("notas", "").strip()
            dias_vigencia = int(request.POST.get("dias_vigencia", "30") or "30")
            fecha_vencimiento_str = request.POST.get("fecha_vencimiento", "").strip()

            if not nombre:
                messages.error(request, "El nombre de la empresa es obligatorio.")
                return redirect("empresas_list")

            if Empresa.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, "Ya existe una empresa con ese nombre.")
                return redirect("empresas_list")

            fecha_pago = timezone.now().date() if activa else None
            fecha_vencimiento = None

            if fecha_vencimiento_str:
                try:
                    fecha_vencimiento = timezone.datetime.strptime(fecha_vencimiento_str, "%Y-%m-%d").date()
                except ValueError:
                    messages.error(request, "Fecha de vencimiento invalida.")
                    return redirect("empresas_list")
            elif activa:
                fecha_vencimiento = fecha_pago + timedelta(days=dias_vigencia)

            Empresa.objects.create(
                nombre=nombre,
                plan=plan,
                activa=activa,
                fecha_pago=fecha_pago,
                fecha_vencimiento=fecha_vencimiento,
                notas=notas,
                creado_por=request.user,
            )
            messages.success(request, "Empresa creada correctamente.")
            return redirect("empresas_list")

        if action == "actualizar_empresa":
            empresa_id = request.POST.get("empresa_id")
            empresa = get_object_or_404(Empresa, id=empresa_id)

            empresa.plan = request.POST.get("plan", empresa.plan).strip() or empresa.plan
            empresa.activa = request.POST.get("activa") == "on"
            empresa.notas = request.POST.get("notas", empresa.notas or "").strip()

            fecha_vencimiento_str = request.POST.get("fecha_vencimiento", "").strip()
            if fecha_vencimiento_str:
                try:
                    empresa.fecha_vencimiento = timezone.datetime.strptime(fecha_vencimiento_str, "%Y-%m-%d").date()
                except ValueError:
                    messages.error(request, "Fecha de vencimiento invalida.")
                    return redirect("empresas_list")

            empresa.save()
            messages.success(request, "Empresa actualizada.")
            return redirect("empresas_list")

        if action == "toggle_empresa":
            empresa_id = request.POST.get("empresa_id")
            empresa = get_object_or_404(Empresa, id=empresa_id)
            empresa.activa = not empresa.activa
            empresa.save(update_fields=["activa"])
            messages.success(request, "Estado de empresa actualizado.")
            return redirect("empresas_list")

    empresas = Empresa.objects.annotate(
        total_usuarios=Count("usuarios", distinct=True),
        pagos_pendientes=Count("pagos", filter=Q(pagos__estado="pendiente"), distinct=True),
    ).order_by("nombre")

    context = {
        "empresas": empresas,
    }
    return render(request, "empresas/empresas/empresas.html", context)


@user_passes_test(lambda user: user.is_superuser)
def clientes_list(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "crear_admin_empresa":
            empresa_id = request.POST.get("empresa_id")
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "").strip()
            email = request.POST.get("email", "").strip()
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()

            if not empresa_id or not username or not password:
                messages.error(request, "Empresa, usuario y password son obligatorios.")
                return redirect("empresas_clientes")

            if User.objects.filter(username=username).exists():
                messages.error(request, "El usuario ya existe.")
                return redirect("empresas_clientes")

            if email and User.objects.filter(email=email).exists():
                messages.error(request, "El email ya esta registrado.")
                return redirect("empresas_clientes")

            empresa = get_object_or_404(Empresa, id=empresa_id)

            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_staff=True,
                is_superuser=False,
            )

            PerfilUsuario.objects.create(
                usuario=usuario,
                empresa=empresa,
                rol="administrador",
                nombre_ubicacion=empresa.nombre,
                activo=True,
                creado_por=request.user,
            )

            messages.success(request, "Admin de empresa creado correctamente.")
            return redirect("empresas_clientes")

        if action == "editar_admin_empresa":
            perfil_id = request.POST.get("perfil_id")
            perfil = get_object_or_404(PerfilUsuario, id=perfil_id, rol="administrador")
            usuario = perfil.usuario

            if usuario:
                usuario.first_name = request.POST.get("first_name", usuario.first_name)
                usuario.last_name = request.POST.get("last_name", usuario.last_name)
                usuario.email = request.POST.get("email", usuario.email)
                usuario.is_active = request.POST.get("activo") == "on"
                nueva_password = request.POST.get("password", "").strip()
                if nueva_password:
                    usuario.set_password(nueva_password)
                usuario.save()

            perfil.activo = usuario.is_active if usuario else perfil.activo
            perfil.save(update_fields=["activo"])

            messages.success(request, "Admin actualizado.")
            return redirect("empresas_clientes")

        if action == "toggle_admin":
            perfil_id = request.POST.get("perfil_id")
            perfil = get_object_or_404(PerfilUsuario, id=perfil_id, rol="administrador")
            if perfil.usuario:
                perfil.usuario.is_active = not perfil.usuario.is_active
                perfil.usuario.save(update_fields=["is_active"])
                perfil.activo = perfil.usuario.is_active
                perfil.save(update_fields=["activo"])
            messages.success(request, "Estado del admin actualizado.")
            return redirect("empresas_clientes")

    empresas = Empresa.objects.order_by("nombre")
    admins = PerfilUsuario.objects.select_related("usuario", "empresa").filter(rol="administrador", empresa__isnull=False)

    context = {
        "empresas": empresas,
        "admins": admins,
    }
    return render(request, "empresas/clientes/clientes.html", context)


@user_passes_test(lambda user: user.is_superuser)
def qr_config(request):
    if request.method == "POST":
        qr_imagen = request.FILES.get("qr_imagen")
        instrucciones = request.POST.get("instrucciones", "").strip()

        if not qr_imagen:
            messages.error(request, "Debes subir una imagen QR.")
            return redirect("empresas_qr")

        PagoQRConfig.objects.filter(activo=True).update(activo=False)
        PagoQRConfig.objects.create(
            nombre="QR Principal",
            qr_imagen=qr_imagen,
            instrucciones=instrucciones,
            activo=True,
            creado_por=request.user,
        )
        messages.success(request, "QR actualizado correctamente.")
        return redirect("empresas_qr")

    qr_actual = PagoQRConfig.objects.filter(activo=True).order_by("-fecha_creacion").first()
    return render(request, "empresas/qr/qr.html", {"qr_config": qr_actual})


@user_passes_test(lambda user: user.is_superuser)
def panel_admin(request):
    return redirect("empresas_list")
