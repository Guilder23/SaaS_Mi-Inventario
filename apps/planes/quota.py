from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from apps.empresas.models import Empresa
from apps.planes.models import Plan, PlanRolLimite


@dataclass(frozen=True)
class PlanLimits:
    codigo: str
    max_productos: Optional[int]
    max_usuarios_total: Optional[int]


def get_plan_for_empresa(empresa: Empresa) -> Optional[Plan]:
    if not empresa or not getattr(empresa, "plan", None):
        return None
    return Plan.objects.filter(codigo=empresa.plan, activo=True).first()


def get_limits_for_empresa(empresa: Empresa) -> Optional[PlanLimits]:
    plan = get_plan_for_empresa(empresa)
    if not plan:
        return None
    return PlanLimits(codigo=plan.codigo, max_productos=plan.max_productos, max_usuarios_total=plan.max_usuarios_total)


def can_create_producto(*, empresa: Empresa) -> tuple[bool, Optional[int], Optional[int]]:
    """Retorna (ok, limite, usados)."""
    plan = get_plan_for_empresa(empresa)
    if not plan or plan.max_productos is None:
        return True, None, None

    from apps.productos.models import Producto

    usados = Producto.all_objects.filter(empresa=empresa).count()
    return usados < plan.max_productos, plan.max_productos, usados


def can_activate_user_for_role(*, empresa: Empresa, rol: str) -> tuple[bool, Optional[int], Optional[int], Optional[int], Optional[int]]:
    """Retorna (ok, limite_total, usados_total, limite_rol, usados_rol)."""
    plan = get_plan_for_empresa(empresa)
    if not plan:
        return True, None, None, None, None

    from apps.usuarios.models import PerfilUsuario

    usados_total = PerfilUsuario.all_objects.filter(
        empresa=empresa,
        activo=True,
        usuario__isnull=False,
        usuario__is_active=True,
    ).count()

    limite_total = plan.max_usuarios_total
    if limite_total is not None and usados_total >= limite_total:
        return False, limite_total, usados_total, None, None

    limite_rol_obj = PlanRolLimite.objects.filter(plan=plan, rol=rol).first()
    limite_rol = limite_rol_obj.max_usuarios if limite_rol_obj else None

    if limite_rol is None:
        return True, limite_total, usados_total, None, None

    usados_rol = PerfilUsuario.all_objects.filter(
        empresa=empresa,
        rol=rol,
        activo=True,
        usuario__isnull=False,
        usuario__is_active=True,
    ).count()

    if usados_rol >= limite_rol:
        return False, limite_total, usados_total, limite_rol, usados_rol

    return True, limite_total, usados_total, limite_rol, usados_rol
