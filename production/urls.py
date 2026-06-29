from django.urls import path

from . import views

app_name = "production"

urlpatterns = [
    path("raw-material/", views.dashboard, name="dashboard"),
    path("raw-material/stok/", views.item_list, name="item_list"),
    path("raw-material/transaksi/", views.movement_list, name="movement_list"),
    path("raw-material/transaksi/baru/", views.movement_create, name="movement_create"),
    path("raw-material/analitik/", views.analytics, name="analytics"),
]
