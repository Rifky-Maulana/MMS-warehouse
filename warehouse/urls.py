from django.urls import path

from . import views

app_name = "warehouse"

urlpatterns = [
    path("gudang/", views.item_list, name="item_list"),
]
