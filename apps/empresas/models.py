from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Empresa(models.Model):
    PLANES = (
        ("basico", "Basico"),
        ("pro", "Pro"),
        ("enterprise", "Enterprise"),
    )

    nombre = models.CharField(max_length=200, unique=True)
    plan = models.CharField(max_length=20, choices=PLANES, default="basico")
    activa = models.BooleanField(default=True)
    fecha_pago = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    @property
    def esta_activa(self):
        if not self.activa:
            return False
        if self.fecha_vencimiento and self.fecha_vencimiento < timezone.now().date():
            return False
        return True


class PagoEmpresa(models.Model):
    ESTADOS = (
        ("pendiente", "Pendiente"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
    )

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="pagos")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=10, default="BOB")

    # Snapshot del plan/precio al momento del pago (para historial/PDF)
    plan_codigo = models.CharField(max_length=30, blank=True, null=True)
    plan_nombre = models.CharField(max_length=100, blank=True, null=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    descuento_monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    comprobante = models.ImageField(upload_to="pagos/", null=False, blank=False)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    dias_vigencia = models.IntegerField(default=30)

    enviado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="pagos_enviados")
    revisado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="pagos_revisados")
    comentario = models.TextField(blank=True, null=True)

    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Pago de Empresa"
        verbose_name_plural = "Pagos de Empresas"
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"{self.empresa.nombre} - {self.monto} {self.moneda}"

    def save(self, *args, **kwargs):
        estado_anterior = None
        if self.pk:
            estado_anterior = PagoEmpresa.objects.filter(pk=self.pk).values_list("estado", flat=True).first()

        super().save(*args, **kwargs)

        if self.estado == "aprobado" and estado_anterior != "aprobado":
            fecha_pago = timezone.now().date()
            self.empresa.fecha_pago = fecha_pago
            self.empresa.fecha_vencimiento = fecha_pago + timedelta(days=self.dias_vigencia)
            self.empresa.activa = True
            self.empresa.save(update_fields=["fecha_pago", "fecha_vencimiento", "activa"])


class PagoQRConfig(models.Model):
    nombre = models.CharField(max_length=200, default="QR Principal")
    qr_imagen = models.ImageField(upload_to="qr/", null=True, blank=True)
    instrucciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Configuracion QR"
        verbose_name_plural = "Configuraciones QR"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.nombre
