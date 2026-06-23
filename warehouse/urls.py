from django.urls import path

from . import views

app_name = "warehouse"

urlpatterns = [
    path("gudang/", views.item_list, name="item_list"),
    path("transaksi/", views.movement_list, name="movement_list"),
    path("transaksi/baru/", views.movement_create, name="movement_create"),
    path("analitik/", views.analytics, name="analytics"),
]
