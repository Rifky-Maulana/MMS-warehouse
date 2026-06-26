from django.conf import settings
from django.db import models


class ProductionCategory(models.Model):
    name = models.CharField("Nama", max_length=100, unique=True)

    class Meta:
        verbose_name = "Kategori Produksi"
        verbose_name_plural = "Kategori Produksi"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductionSupplier(models.Model):
    name = models.CharField("Nama", max_length=150)
    contact = models.CharField("Kontak", max_length=150, blank=True)

    class Meta:
        verbose_name = "Supplier Produksi"
        verbose_name_plural = "Supplier Produksi"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductionItem(models.Model):
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
        related_name="production_items",
        verbose_name="Lokasi",
    )
    category = models.ForeignKey(
        ProductionCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="items", verbose_name="Kategori",
    )
    unit = models.CharField("Satuan", max_length=10, choices=Unit.choices, default=Unit.PCS)
    current_stock = models.PositiveIntegerField("Stok Saat Ini", default=0)
    min_stock = models.PositiveIntegerField("Stok Minimum", default=0)
    is_active = models.BooleanField(
        "Aktif", default=True,
        help_text="Hilangkan centang untuk menonaktifkan barang (disembunyikan dari daftar, "
                  "tanpa menghapus data & riwayatnya).",
    )
    created_at = models.DateTimeField("Dibuat", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui", auto_now=True)

    class Meta:
        verbose_name = "Barang Produksi"
        verbose_name_plural = "Barang Produksi"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["location", "sku"], name="uniq_production_item_sku_per_location"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self) -> bool:
        return self.current_stock <= self.min_stock


class ProductionMovement(models.Model):
    class Type(models.TextChoices):
        IN = "in", "Masuk"
        OUT = "out", "Keluar"
        ADJUSTMENT = "adjustment", "Penyesuaian"

    item = models.ForeignKey(
        ProductionItem, on_delete=models.PROTECT, related_name="movements", verbose_name="Barang",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="production_movements", verbose_name="Pencatat",
    )
    supplier = models.ForeignKey(
        ProductionSupplier, on_delete=models.SET_NULL, null=True, blank=True,
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
        verbose_name = "Transaksi Produksi"
        verbose_name_plural = "Transaksi Produksi"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} {self.quantity} × {self.item.name}"
