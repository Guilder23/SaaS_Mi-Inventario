from __future__ import annotations

from apps.planes.models import Plan


def theme_flags(request):
    """Flags de UI globales (tema claro/oscuro).

    - Superusuario: siempre permitido.
    - Usuarios normales: depende del plan de la empresa activa.
    """

    theme_allowed = True

    try:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return {"theme_allowed": True}

        if user.is_superuser:
            return {"theme_allowed": True}

        empresa = getattr(request, "empresa", None)
        if not empresa:
            return {"theme_allowed": True}

        plan = (
            Plan.objects.filter(codigo=empresa.plan, activo=True)
            .only("permite_modo_oscuro")
            .first()
        )
        if plan is not None:
            theme_allowed = bool(plan.permite_modo_oscuro)

    except Exception:
        # No bloquear la UI si hay algún error inesperado.
        theme_allowed = True

    return {"theme_allowed": theme_allowed}
