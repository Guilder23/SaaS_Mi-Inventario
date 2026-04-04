from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from apps.planes.models import Plan, PlanRolLimite


@user_passes_test(lambda user: user.is_superuser)
def planes_list(request):
    roles = PlanRolLimite.ROLES

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "crear_plan":
            codigo = (request.POST.get("codigo") or "").strip().lower()
            nombre = (request.POST.get("nombre") or "").strip()
            max_productos = (request.POST.get("max_productos") or "").strip()
            max_usuarios_total = (request.POST.get("max_usuarios_total") or "").strip()
            activo = request.POST.get("activo") == "on"

            if not codigo or not nombre:
                messages.error(request, "Código y nombre son obligatorios.")
                return redirect("planes_list")

            if Plan.objects.filter(codigo=codigo).exists():
                messages.error(request, "Ya existe un plan con ese código.")
                return redirect("planes_list")

            plan = Plan.objects.create(
                codigo=codigo,
                nombre=nombre,
                max_productos=int(max_productos) if max_productos else None,
                max_usuarios_total=int(max_usuarios_total) if max_usuarios_total else None,
                activo=activo,
            )

            for rol, _label in roles:
                PlanRolLimite.objects.get_or_create(plan=plan, rol=rol)

            messages.success(request, "Plan creado correctamente.")
            return redirect("planes_list")

        if action == "editar_plan":
            plan_id = request.POST.get("plan_id")
            plan = get_object_or_404(Plan, id=plan_id)

            plan.nombre = (request.POST.get("nombre") or "").strip() or plan.nombre

            max_productos = (request.POST.get("max_productos") or "").strip()
            max_usuarios_total = (request.POST.get("max_usuarios_total") or "").strip()
            plan.max_productos = int(max_productos) if max_productos else None
            plan.max_usuarios_total = int(max_usuarios_total) if max_usuarios_total else None
            plan.activo = request.POST.get("activo") == "on"
            plan.save()

            # asegurar filas por rol
            for rol, _label in roles:
                PlanRolLimite.objects.get_or_create(plan=plan, rol=rol)

            messages.success(request, "Plan actualizado.")
            return redirect("planes_list")

        if action == "guardar_roles":
            plan_id = request.POST.get("plan_id")
            plan = get_object_or_404(Plan, id=plan_id)

            for rol, _label in roles:
                key = f"max_usuarios__{rol}"
                valor = (request.POST.get(key) or "").strip()
                limite, _created = PlanRolLimite.objects.get_or_create(plan=plan, rol=rol)
                limite.max_usuarios = int(valor) if valor else None
                limite.save(update_fields=["max_usuarios"])

            messages.success(request, "Límites por rol guardados.")
            return redirect("planes_list")

        if action == "toggle_plan":
            plan_id = request.POST.get("plan_id")
            plan = get_object_or_404(Plan, id=plan_id)
            plan.activo = not plan.activo
            plan.save(update_fields=["activo", "fecha_actualizacion"])

            messages.success(request, "Plan activado." if plan.activo else "Plan desactivado.")
            return redirect("planes_list")

    planes = Plan.objects.prefetch_related("limites_roles").order_by("codigo")

    # Map plan_id -> {rol: max}
    limites_por_plan = {}
    for plan in planes:
        limites_por_plan[plan.id] = {lr.rol: lr.max_usuarios for lr in plan.limites_roles.all()}

    context = {
        "planes": planes,
        "roles": roles,
        "limites_por_plan": limites_por_plan,
    }
    return render(request, "planes/planes.html", context)
