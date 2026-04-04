from django.db import models


class Plan(models.Model):
    """Configuración global de planes (cuotas SaaS)."""

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)

    # Cuotas
    max_productos = models.PositiveIntegerField(null=True, blank=True, help_text="Límite de productos activos/registrados. Vacío = ilimitado")
    max_usuarios_total = models.PositiveIntegerField(null=True, blank=True, help_text="Límite total de usuarios activos. Vacío = ilimitado")

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


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
