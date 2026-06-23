from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField("Nama", max_length=100, unique=True)

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategori"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField("Nama", max_length=150)
    contact = models.CharField("Kontak", max_length=150, blank=True)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Supplier"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Item(models.Model):
    class Unit(models.TextChoices):
        PCS = "pcs", "Pcs"
        BOX = "box", "Box"
        KG = "kg", "Kg"
        LITER = "liter", "Liter"
        PACK = "pack", "Pack"

    # SKU unik PER LOKASI (lihat Meta.constraints), jadi kode yang sama
    # boleh dipakai di lokasi berbeda.
    sku = models.CharField("Kode (SKU)", max_length=50)
    name = models.CharField("Nama", max_length=200)
    location = models.ForeignKey(
        "core.Location",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="items",
        verbose_name="Lokasi",
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="items", verbose_name="Kategori",
    )
    unit = models.CharField("Satuan", max_length=10, choices=Unit.choices, default=Unit.PCS)
    current_stock = models.PositiveIntegerField("Stok Saat Ini", default=0)
    min_stock = models.PositiveIntegerField("Stok Minimum", default=0)
    created_at = models.DateTimeField("Dibuat", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui", auto_now=True)

    class Meta:
        verbose_name = "Barang"
        verbose_name_plural = "Barang"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["location", "sku"], name="uniq_item_sku_per_location"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self) -> bool:
        return self.current_stock <= self.min_stock


class StockMovement(models.Model):
    class Type(models.TextChoices):
        IN = "in", "Masuk"
        OUT = "out", "Keluar"
        ADJUSTMENT = "adjustment", "Penyesuaian"

    item = models.ForeignKey(
        Item, on_delete=models.PROTECT, related_name="movements", verbose_name="Barang",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="stock_movements", verbose_name="Pencatat",
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="movements", verbose_name="Supplier",
    )
    type = models.CharField("Jenis", max_length=12, choices=Type.choices)
    quantity = models.PositiveIntegerField(
        "Jumlah",
        help_text="Untuk Masuk/Keluar: jumlah yang bergerak. "
                  "Untuk Penyesuaian: jumlah stok yang sebenarnya (hasil hitung fisik).",
    )
    note = models.CharField("Catatan", max_length=255, blank=True)
    reference = models.CharField("No. Referensi", max_length=100, blank=True)
    created_at = models.DateTimeField("Waktu", auto_now_add=True)

    class Meta:
        verbose_name = "Transaksi Stok"
        verbose_name_plural = "Transaksi Stok"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} {self.quantity} × {self.item.name}"
