from django.contrib import admin

from .models import Category, Item, Supplier


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact")
    search_fields = ("name", "contact")


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "name",
        "category",
        "unit",
        "current_stock",
        "min_stock",
        "stok_menipis",
    )
    list_filter = ("category", "unit")
    search_fields = ("sku", "name")
    list_select_related = ("category",)

    @admin.display(boolean=True, description="Stok menipis?")
    def stok_menipis(self, obj):
        return obj.is_low_stock
