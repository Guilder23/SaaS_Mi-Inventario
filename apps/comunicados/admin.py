from django.contrib import admin

from .models import Comunicado, ComunicadoLectura


@admin.register(Comunicado)
class ComunicadoAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "publicado", "activo", "fecha_publicacion", "fecha_creacion")
    list_filter = ("publicado", "activo")
    search_fields = ("titulo", "mensaje")
    readonly_fields = ("fecha_creacion", "fecha_actualizacion")


@admin.register(ComunicadoLectura)
class ComunicadoLecturaAdmin(admin.ModelAdmin):
    list_display = ("id", "comunicado", "usuario", "fecha_lectura")
    list_filter = ("fecha_lectura",)
    search_fields = ("comunicado__titulo", "usuario__username", "usuario__email")
