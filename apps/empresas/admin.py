from django.contrib import admin

from .models import Empresa, PagoEmpresa, PagoQRConfig


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "plan", "activa", "fecha_vencimiento"]
    list_filter = ["plan", "activa"]
    search_fields = ["nombre"]


@admin.register(PagoEmpresa)
class PagoEmpresaAdmin(admin.ModelAdmin):
    list_display = ["empresa", "monto", "moneda", "estado", "fecha_envio"]
    list_filter = ["estado", "moneda"]
    search_fields = ["empresa__nombre"]


@admin.register(PagoQRConfig)
class PagoQRConfigAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activo", "fecha_creacion"]
    list_filter = ["activo"]
    search_fields = ["nombre"]
