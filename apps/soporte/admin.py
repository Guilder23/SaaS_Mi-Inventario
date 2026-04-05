from django.contrib import admin

from .models import MensajeTicket, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("codigo", "asunto", "empresa", "creado_por", "estado", "prioridad", "fecha_actualizacion")
    list_filter = ("estado", "prioridad", "categoria")
    search_fields = ("codigo", "asunto", "empresa__nombre", "creado_por__username")
    ordering = ("-fecha_actualizacion",)


@admin.register(MensajeTicket)
class MensajeTicketAdmin(admin.ModelAdmin):
    list_display = ("ticket", "autor", "rol", "creado_en")
    list_filter = ("rol",)
    search_fields = ("ticket__codigo", "autor__username", "contenido")
    ordering = ("-creado_en",)
