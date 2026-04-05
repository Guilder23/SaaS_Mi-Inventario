import secrets

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from apps.core.tenancy import EmpresaOwnedModel


class Ticket(EmpresaOwnedModel):
    CATEGORIAS = (
        ("tecnico", "Tecnico"),
        ("facturacion", "Facturacion"),
        ("sugerencia", "Sugerencia"),
        ("ayuda", "Ayuda de uso"),
    )

    PRIORIDADES = (
        ("baja", "Baja"),
        ("media", "Media"),
        ("alta", "Alta"),
        ("critica", "Critica"),
    )

    ESTADOS = (
        ("abierto", "Abierto"),
        ("en_proceso", "En proceso"),
        ("respondido", "Respondido"),
        ("cerrado", "Cerrado"),
    )

    ULTIMO_ROL = (
        ("cliente", "Cliente"),
        ("soporte", "Soporte"),
        ("sistema", "Sistema"),
    )

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tickets",
    )
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_creados",
    )
    asignado_a = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_asignados",
    )
    asunto = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="tecnico")
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default="media")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="abierto")
    codigo = models.CharField(max_length=12, unique=True, blank=True)
    ultimo_mensaje_por = models.CharField(max_length=20, choices=ULTIMO_ROL, default="cliente")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Ticket de soporte"
        verbose_name_plural = "Tickets de soporte"
        ordering = ["-fecha_actualizacion", "-fecha_creacion"]

    def __str__(self):
        return f"{self.codigo} - {self.asunto}"

    def _generar_codigo_unico(self):
        codigo = f"TK-{secrets.token_hex(3).upper()}"
        while Ticket.all_objects.filter(codigo=codigo).exists():
            codigo = f"TK-{secrets.token_hex(3).upper()}"
        return codigo

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._generar_codigo_unico()

        if self.estado == "cerrado" and self.fecha_cierre is None:
            self.fecha_cierre = timezone.now()
        if self.estado != "cerrado" and self.fecha_cierre is not None:
            self.fecha_cierre = None

        super().save(*args, **kwargs)


class MensajeTicket(EmpresaOwnedModel):
    ROLES = (
        ("cliente", "Cliente"),
        ("soporte", "Soporte"),
        ("sistema", "Sistema"),
    )

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="mensajes_soporte",
    )
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="mensajes")
    autor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mensajes_soporte",
    )
    rol = models.CharField(max_length=20, choices=ROLES, default="cliente")
    contenido = models.TextField(blank=True)
    adjunto = models.FileField(upload_to="soporte/adjuntos/", null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje de ticket"
        verbose_name_plural = "Mensajes de ticket"
        ordering = ["creado_en"]

    def __str__(self):
        autor = self.autor.username if self.autor else "Sistema"
        return f"{self.ticket.codigo} - {autor}"

    def save(self, *args, **kwargs):
        if not self.empresa_id and self.ticket_id:
            self.empresa = self.ticket.empresa
        super().save(*args, **kwargs)
