from django.urls import path

from . import views

urlpatterns = [
    path("pagos/", views.pagos_empresa, name="pagos_empresa"),
    path("pagos-admin/", views.pagos_admin, name="pagos_admin"),
    path("pagos/<int:pago_id>/pdf/", views.pago_pdf, name="pago_pdf"),
    path("panel/", views.panel_admin, name="empresas_panel"),
    path("empresas/", views.empresas_list, name="empresas_list"),
    path("clientes/", views.clientes_list, name="empresas_clientes"),
    path("qr/", views.qr_config, name="empresas_qr"),
]
