from django.conf import settings
from django.db import models
from django.utils import timezone


class Comunicado(models.Model):
    """Comunicado global (broadcast) visible para todos los usuarios."""

    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()

    publicado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    fecha_publicacion = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comunicados_creados",
    )

    class Meta:
        ordering = ["-fecha_publicacion", "-fecha_creacion"]
        verbose_name = "Comunicado"
        verbose_name_plural = "Comunicados"

    def __str__(self) -> str:
        return self.titulo

    def publicar_ahora(self):
        if not self.publicado:
            self.publicado = True
        if not self.fecha_publicacion:
            self.fecha_publicacion = timezone.now()
        self.save(update_fields=["publicado", "fecha_publicacion", "fecha_actualizacion"])

    def despublicar(self):
        if self.publicado:
            self.publicado = False
            self.save(update_fields=["publicado", "fecha_actualizacion"])


class ComunicadoLectura(models.Model):
    comunicado = models.ForeignKey(
        Comunicado,
        on_delete=models.CASCADE,
        related_name="lecturas",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lecturas_comunicados",
    )
    fecha_lectura = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("comunicado", "usuario")
        verbose_name = "Lectura de comunicado"
        verbose_name_plural = "Lecturas de comunicados"

    def __str__(self) -> str:
        return f"{self.usuario_id} -> {self.comunicado_id}"
