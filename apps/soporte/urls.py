from django.urls import path

from . import views

urlpatterns = [
    path("", views.tickets_list, name="soporte_tickets"),
    path("admin/", views.tickets_admin_list, name="soporte_admin_list"),
    path("ticket/<int:ticket_id>/", views.ticket_detalle, name="soporte_ticket_detalle"),
]
