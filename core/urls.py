from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("beranda/", views.no_access, name="no_access"),
]
