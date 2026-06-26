from django.urls import path

from . import views

app_name = "production"

urlpatterns = [
    path("produksi/", views.dashboard, name="dashboard"),
    path("produksi/stok/", views.item_list, name="item_list"),
    path("produksi/transaksi/", views.movement_list, name="movement_list"),
    path("produksi/transaksi/baru/", views.movement_create, name="movement_create"),
    path("produksi/analitik/", views.analytics, name="analytics"),
]
