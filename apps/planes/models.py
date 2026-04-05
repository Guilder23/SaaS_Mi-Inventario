from decimal import Decimal

from django.db import models
from django.utils import timezone


class Plan(models.Model):
    """Configuración global de planes (cuotas SaaS)."""

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)

    # Cuotas
    max_productos = models.PositiveIntegerField(null=True, blank=True, help_text="Límite de productos activos/registrados. Vacío = ilimitado")
    max_usuarios_total = models.PositiveIntegerField(null=True, blank=True, help_text="Límite total de usuarios activos. Vacío = ilimitado")

    # Features
    permite_modo_oscuro = models.BooleanField(
        default=True,
        help_text="Permite usar el modo oscuro/claro en la interfaz.",
    )

    activo = models.BooleanField(default=True)

    # Precios
    precio_mensual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Precio mensual del plan. Vacío = no configurado.",
    )
    moneda = models.CharField(max_length=10, default="BOB")

    # Descuento simple por meses (ej. diciembre = navidad)
    descuento_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Porcentaje de descuento (0-100).",
    )
    descuento_meses = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Meses (1-12) separados por coma donde aplica el descuento. Ej: 12",
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def _meses_descuento_set(self):
        if not self.descuento_meses:
            return set()
        meses = set()
        for raw in str(self.descuento_meses).split(","):
            raw = raw.strip()
            if not raw:
                continue
            try:
                m = int(raw)
            except (TypeError, ValueError):
                continue
            if 1 <= m <= 12:
                meses.add(m)
        return meses

    def descuento_aplica(self, fecha=None):
        if self.precio_mensual is None:
            return False
        if not self.descuento_porcentaje or self.descuento_porcentaje <= 0:
            return False
        fecha = fecha or timezone.now().date()
        return fecha.month in self._meses_descuento_set()

    def calcular_precio(self, fecha=None):
        """Devuelve desglose de precio (base, descuento y total)."""
        fecha = fecha or timezone.now().date()
        base = self.precio_mensual if self.precio_mensual is not None else Decimal("0.00")
        base = Decimal(base)

        aplica = self.descuento_aplica(fecha=fecha)
        porcentaje = Decimal(self.descuento_porcentaje or 0)
        if aplica and porcentaje > 0:
            descuento = (base * porcentaje / Decimal("100")).quantize(Decimal("0.01"))
        else:
            descuento = Decimal("0.00")
            porcentaje = Decimal("0.00")

        total = (base - descuento).quantize(Decimal("0.01"))
        return {
            "fecha": fecha,
            "moneda": (self.moneda or "BOB").strip() or "BOB",
            "base": base.quantize(Decimal("0.01")),
            "descuento_porcentaje": porcentaje.quantize(Decimal("0.01")),
            "descuento": descuento,
            "total": total,
            "aplica_descuento": aplica,
        }


class PlanRolLimite(models.Model):
    ROLES = (
        ("administrador", "Administrador"),
        ("almacen", "Almacén"),
        ("tienda", "Tienda"),
        ("deposito", "Depósito"),
        ("tienda_online", "Tienda Online"),
    )

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="limites_roles")
    rol = models.CharField(max_length=20, choices=ROLES)

    # Vacío = ilimitado
    max_usuarios = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Límite por rol"
        verbose_name_plural = "Límites por rol"
        unique_together = ("plan", "rol")
        ordering = ["plan__codigo", "rol"]

    def __str__(self):
        return f"{self.plan.codigo} / {self.rol}: {self.max_usuarios if self.max_usuarios is not None else 'ilimitado'}"
