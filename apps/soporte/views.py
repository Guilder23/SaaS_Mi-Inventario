from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.notificaciones.models import Notificacion

from .models import MensajeTicket, Ticket


def es_soporte(user):
    """Define quién es el equipo de soporte.

    Importante: en este proyecto algunos "admins de empresa" pueden tener is_staff=True,
    pero NO deben ver el panel global de soporte.

    Regla:
    - Soporte: superuser, o staff sin empresa asignada (o sin perfil).
    - Cliente: cualquier usuario con empresa (incluye admin de empresa aunque sea staff).
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    if not user.is_staff:
        return False

    perfil = getattr(user, "perfil", None)
    empresa = getattr(perfil, "empresa", None) if perfil else None
    return empresa is None


def soporte_users_queryset():
    """Usuarios que deben recibir notificaciones de soporte (equipo interno)."""
    from django.contrib.auth.models import User

    return User.objects.filter(
        Q(is_superuser=True)
        | (Q(is_staff=True) & (Q(perfil__isnull=True) | Q(perfil__empresa__isnull=True)))
    ).distinct()


@login_required
def tickets_list(request):
    if es_soporte(request.user):
        return redirect("soporte_admin_list")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "crear_ticket":
            asunto = (request.POST.get("asunto") or "").strip()
            categoria = request.POST.get("categoria") or "tecnico"
            prioridad = request.POST.get("prioridad") or "media"
            mensaje = (request.POST.get("mensaje") or "").strip()
            adjunto = request.FILES.get("adjunto")

            if not asunto:
                messages.error(request, "El asunto es obligatorio.")
                return redirect("soporte_tickets")

            if not mensaje and not adjunto:
                messages.error(request, "Debes escribir un mensaje o adjuntar un archivo.")
                return redirect("soporte_tickets")

            if categoria not in dict(Ticket.CATEGORIAS):
                categoria = "tecnico"
            if prioridad not in dict(Ticket.PRIORIDADES):
                prioridad = "media"

            empresa = None
            if hasattr(request.user, "perfil"):
                empresa = request.user.perfil.empresa

            ticket = Ticket.objects.create(
                empresa=empresa,
                creado_por=request.user,
                asunto=asunto,
                categoria=categoria,
                prioridad=prioridad,
                estado="abierto",
                ultimo_mensaje_por="cliente",
            )

            MensajeTicket.objects.create(
                ticket=ticket,
                autor=request.user,
                rol="cliente",
                contenido=mensaje,
                adjunto=adjunto,
                empresa=empresa,
            )

            # Notificar al equipo de soporte
            try:
                soporte_users = soporte_users_queryset()
                ticket_url = reverse("soporte_ticket_detalle", args=[ticket.id])
                empresa_nombre = empresa.nombre if empresa else "-"
                for u in soporte_users:
                    Notificacion.objects.create(
                        usuario=u,
                        tipo="soporte",
                        titulo=f"Nuevo ticket {ticket.codigo}",
                        mensaje=f"Empresa: {empresa_nombre} | Asunto: {ticket.asunto}",
                        url=ticket_url,
                        empresa=empresa,
                    )
            except Exception:
                # Si falla notificaciones, no debe romper el flujo del ticket
                pass

            messages.success(request, "Ticket creado. Nuestro equipo revisara tu mensaje.")
            return redirect("soporte_ticket_detalle", ticket_id=ticket.id)

    tickets = Ticket.objects.filter(creado_por=request.user).order_by("-fecha_actualizacion")

    context = {
        "tickets": tickets,
        "categorias": Ticket.CATEGORIAS,
        "prioridades": Ticket.PRIORIDADES,
    }
    return render(request, "soporte/tickets.html", context)


@login_required
@user_passes_test(es_soporte)
def tickets_admin_list(request):
    tickets = Ticket.all_objects.select_related("empresa", "creado_por", "asignado_a").all()

    estado = (request.GET.get("estado") or "").strip()
    if estado in dict(Ticket.ESTADOS):
        tickets = tickets.filter(estado=estado)

    q = (request.GET.get("q") or "").strip()
    if q:
        tickets = tickets.filter(
            Q(codigo__icontains=q)
            | Q(asunto__icontains=q)
            | Q(empresa__nombre__icontains=q)
            | Q(creado_por__username__icontains=q)
        )

    tickets = tickets.order_by("-fecha_actualizacion")

    context = {
        "tickets": tickets,
        "estados": Ticket.ESTADOS,
        "estado_actual": estado,
        "query": q,
    }
    return render(request, "soporte/admin_tickets.html", context)


@login_required
def ticket_detalle(request, ticket_id: int):
    es_admin = es_soporte(request.user)

    ticket_qs = Ticket.all_objects if es_admin else Ticket.objects
    ticket = get_object_or_404(ticket_qs, id=ticket_id)

    if not es_admin and ticket.creado_por_id != request.user.id:
        messages.error(request, "No tienes permiso para ver este ticket.")
        return redirect("soporte_tickets")

    # Si el usuario abre el ticket, marcar como leídas las notificaciones de soporte asociadas
    try:
        ticket_url = reverse("soporte_ticket_detalle", args=[ticket.id])
        Notificacion.objects.filter(
            usuario=request.user,
            tipo="soporte",
            leida=False,
            url=ticket_url,
        ).update(leida=True, fecha_lectura=timezone.now())
    except Exception:
        pass

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "enviar_mensaje":
            contenido = (request.POST.get("mensaje") or "").strip()
            adjunto = request.FILES.get("adjunto")

            if not contenido and not adjunto:
                messages.error(request, "Debes escribir un mensaje o adjuntar un archivo.")
                return redirect("soporte_ticket_detalle", ticket_id=ticket.id)

            rol = "soporte" if es_admin else "cliente"
            MensajeTicket.objects.create(
                ticket=ticket,
                autor=request.user,
                rol=rol,
                contenido=contenido,
                adjunto=adjunto,
                empresa=ticket.empresa,
            )

            # Notificaciones segun quien escribe
            try:
                ticket_url = reverse("soporte_ticket_detalle", args=[ticket.id])

                if es_admin:
                    if ticket.creado_por_id:
                        Notificacion.objects.create(
                            usuario=ticket.creado_por,
                            tipo="soporte",
                            titulo=f"Respuesta en tu ticket {ticket.codigo}",
                            mensaje=f"Soporte respondio: {ticket.asunto}",
                            url=ticket_url,
                            empresa=ticket.empresa,
                        )
                else:
                    soporte_users = soporte_users_queryset()
                    empresa_nombre = ticket.empresa.nombre if ticket.empresa else "-"
                    for u in soporte_users:
                        Notificacion.objects.create(
                            usuario=u,
                            tipo="soporte",
                            titulo=f"Nuevo mensaje en {ticket.codigo}",
                            mensaje=f"Empresa: {empresa_nombre} | Asunto: {ticket.asunto}",
                            url=ticket_url,
                            empresa=ticket.empresa,
                        )
            except Exception:
                pass

            if es_admin and ticket.estado != "cerrado":
                ticket.estado = "respondido"
            if not es_admin and ticket.estado == "cerrado":
                ticket.estado = "abierto"

            ticket.ultimo_mensaje_por = rol
            ticket.fecha_actualizacion = timezone.now()
            ticket.save(update_fields=["estado", "ultimo_mensaje_por", "fecha_actualizacion", "fecha_cierre"])

            messages.success(request, "Mensaje enviado.")
            return redirect("soporte_ticket_detalle", ticket_id=ticket.id)

        if action == "actualizar_ticket" and es_admin:
            estado = request.POST.get("estado")
            prioridad = request.POST.get("prioridad")
            asignado_id = request.POST.get("asignado_a")

            if estado in dict(Ticket.ESTADOS):
                ticket.estado = estado
            if prioridad in dict(Ticket.PRIORIDADES):
                ticket.prioridad = prioridad

            if asignado_id:
                ticket.asignado_a_id = asignado_id
            else:
                ticket.asignado_a = None

            ticket.fecha_actualizacion = timezone.now()
            ticket.save(update_fields=["estado", "prioridad", "asignado_a", "fecha_actualizacion", "fecha_cierre"])
            messages.success(request, "Ticket actualizado.")
            return redirect("soporte_ticket_detalle", ticket_id=ticket.id)

    mensajes_qs = MensajeTicket.all_objects if es_admin else MensajeTicket.objects
    mensajes = mensajes_qs.filter(ticket=ticket).select_related("autor")
    soporte_users = []
    if es_admin:
        from django.contrib.auth.models import User

        soporte_users = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).order_by("username")

    context = {
        "ticket": ticket,
        "mensajes": mensajes,
        "es_admin": es_admin,
        "estados": Ticket.ESTADOS,
        "prioridades": Ticket.PRIORIDADES,
        "soporte_users": soporte_users,
    }
    return render(request, "soporte/ticket_detalle.html", context)
