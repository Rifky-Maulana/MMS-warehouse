from django import forms
from django.contrib import admin

from .models import Category, Item, StockMovement, Supplier
from .services import apply_movement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact")
    search_fields = ("name", "contact")


@admin.action(description="Aktifkan barang terpilih")
def aktifkan(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Nonaktifkan barang terpilih")
def nonaktifkan(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "sku", "name", "location", "category", "unit",
        "current_stock", "min_stock", "is_active", "stok_menipis",
    )
    list_filter = ("is_active", "location", "category", "unit")
    search_fields = ("sku", "name")
    list_select_related = ("category", "location")
    readonly_fields = ("current_stock",)
    actions = [aktifkan, nonaktifkan]

    @admin.display(boolean=True, description="Stok menipis?")
    def stok_menipis(self, obj):
        return obj.is_low_stock

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(location__in=request.user.locations.all())
        return qs


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ("item", "supplier", "type", "quantity", "note", "reference")

    def clean(self):
        cleaned = super().clean()
        mtype = cleaned.get("type")
        qty = cleaned.get("quantity")
        item = cleaned.get("item")
        if mtype in (StockMovement.Type.IN, StockMovement.Type.OUT) and qty == 0:
            raise forms.ValidationError("Jumlah untuk barang masuk/keluar harus lebih dari 0.")
        if mtype == StockMovement.Type.OUT and item and qty:
            if qty > item.current_stock:
                raise forms.ValidationError(
                    f"Stok tidak cukup. Stok '{item.name}' saat ini "
                    f"{item.current_stock}, diminta keluar {qty}."
                )
        return cleaned


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    form = StockMovementForm
    list_display = ("created_at", "type", "item", "lokasi", "quantity", "user", "supplier", "reference")
    list_filter = ("type", "created_at", "item__location")
    search_fields = ("item__name", "item__sku", "reference", "note")
    list_select_related = ("item", "item__location", "user", "supplier")
    autocomplete_fields = ("item", "supplier")

    @admin.display(description="Lokasi", ordering="item__location")
    def lokasi(self, obj):
        return obj.item.location or "-"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(item__location__in=request.user.locations.all())
        return qs

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("item", "user", "supplier", "type",
                    "quantity", "note", "reference", "created_at")
        return ()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            return
        obj.user = request.user
        apply_movement(obj)
