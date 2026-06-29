from django.urls import path

from . import views

app_name = "mesin"

urlpatterns = [
    path("produksi/<str:kode>/", views.machine_page, name="machine_page"),
]
