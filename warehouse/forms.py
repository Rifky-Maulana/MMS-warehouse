from django import forms

from .models import Item, StockMovement


class MovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ("item", "type", "quantity", "supplier", "note", "reference")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        items = Item.objects.filter(is_active=True)
        if user is not None and not user.is_superuser:
            items = items.filter(location__in=user.locations.all())
        self.fields["item"].queryset = items.select_related("location").order_by("name")
        self.fields["supplier"].required = False
        css = "w-full bg-brand-soft rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-brand/30"
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", css)

    def clean(self):
        cleaned = super().clean()
        mtype = cleaned.get("type")
        qty = cleaned.get("quantity")
        item = cleaned.get("item")
        if mtype in (StockMovement.Type.IN, StockMovement.Type.OUT) and qty == 0:
            raise forms.ValidationError("Jumlah untuk barang masuk/keluar harus lebih dari 0.")
        if mtype == StockMovement.Type.OUT and item and qty and qty > item.current_stock:
            raise forms.ValidationError(
                f"Stok tidak cukup. Stok '{item.name}' saat ini "
                f"{item.current_stock}, diminta keluar {qty}."
            )
        return cleaned
