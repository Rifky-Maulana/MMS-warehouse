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


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "sku", "name", "category", "unit",
        "current_stock", "min_stock", "stok_menipis",
    )
    list_filter = ("category", "unit")
    search_fields = ("sku", "name")
    list_select_related = ("category",)
    # Stok Saat Ini hanya berubah lewat Transaksi Stok, bukan diketik manual.
    readonly_fields = ("current_stock",)

    @admin.display(boolean=True, description="Stok menipis?")
    def stok_menipis(self, obj):
        return obj.is_low_stock


class StockMovementForm(forms.ModelForm):
    """Form transaksi + validasi stok agar pesan error tampil rapi di admin."""

    class Meta:
        model = StockMovement
        fields = ("item", "supplier", "type", "quantity", "note", "reference")

    def clean(self):
        cleaned = super().clean()
        mtype = cleaned.get("type")
        qty = cleaned.get("quantity")
        item = cleaned.get("item")

        if mtype in (StockMovement.Type.IN, StockMovement.Type.OUT) and qty == 0:
            raise forms.ValidationError(
                "Jumlah untuk barang masuk/keluar harus lebih dari 0."
            )

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
    list_display = (
        "created_at", "type", "item", "quantity", "user", "supplier", "reference",
    )
    list_filter = ("type", "created_at", "item")
    search_fields = ("item__name", "item__sku", "reference", "note")
    list_select_related = ("item", "user", "supplier")
    autocomplete_fields = ("item", "supplier")

    def get_readonly_fields(self, request, obj=None):
        # Transaksi yang sudah ada bersifat permanen — semua field jadi read-only.
        if obj:
            return ("item", "user", "supplier", "type",
                    "quantity", "note", "reference", "created_at")
        return ()

    def has_delete_permission(self, request, obj=None):
        # Riwayat transaksi tidak boleh dihapus (menjaga konsistensi stok).
        return False

    def save_model(self, request, obj, form, change):
        if change:
            return  # transaksi lama tidak diubah
        obj.user = request.user
        # Validasi + perbarui stok + simpan, semuanya atomic.
        apply_movement(obj)
