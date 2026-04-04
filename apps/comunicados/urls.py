from django.urls import path

from . import views

urlpatterns = [
    path('', views.comunicados_list, name='comunicados_list'),
    path('historial/', views.historial_comunicados, name='comunicados_historial'),
    path('<int:id>/', views.detalle_comunicado, name='comunicado_detalle'),
    path('obtener/', views.obtener_comunicados, name='obtener_comunicados'),
    path('contador/', views.contador_comunicados, name='contador_comunicados'),
    path('marcar-leida/<int:id>/', views.marcar_comunicado_leido, name='marcar_comunicado_leido'),
    path('marcar-todos-leidos/', views.marcar_todos_comunicados_leidos, name='marcar_todos_comunicados_leidos'),
]
