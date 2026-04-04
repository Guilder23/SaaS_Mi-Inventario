from django.urls import path

from . import views

urlpatterns = [
    path("", views.planes_list, name="planes_list"),
]
