from datetime import date, datetime, timedelta

from django.conf import settings
from django.db import models

from .machines import get_machine


# ===== Konfigurasi per JENIS mesin =====
# Field khusus tiap jenis (disimpan di kolom JSON `detail`).
# Tipe: "decimal" (angka), "lulus" (pilihan Lulus/Gagal).
JENIS_DETAIL_FIELDS = {
    "MIXING": [
        ("pp_murni_kg", "PP murni (kg)", "decimal"),
        ("bahan_daur_ulang_kg", "Bahan daur ulang (kg)", "decimal"),
    ],
    "CRUSHING": [],
    "INJECTION": [
        ("suhu_injector_c", "Suhu injector (°C)", "decimal"),
    ],
    "COUNTING": [],
    "STERILIZATION": [
        ("chemical_indicator", "Chemical indicator", "lulus"),
        ("bio_indicator", "Bio indicator", "lulus"),
    ],
}

# Field umum mana yang DITAMPILKAN per jenis (selain field umum wajib).
JENIS_COMMON_FIELDS = {
    "MIXING":        {"input": False, "output": True, "scrap": False, "defect_ng": False},
    "CRUSHING":      {"input": True,  "output": True, "scrap": True,  "defect_ng": False},
    "INJECTION":     {"input": False, "output": True, "scrap": False, "defect_ng": True},
    "COUNTING":      {"input": False, "output": True, "scrap": False, "defect_ng": True},
    "STERILIZATION": {"input": False, "output": True, "scrap": False, "defect_ng": False},
}


class CatatanProduksi(models.Model):
    class Shift(models.TextChoices):
        S1 = "1", "Shift 1"
        S2 = "2", "Shift 2"
        S3 = "3", "Shift 3"

    # Kode mesin dari registry kode (mesin/machines.py), bukan FK ke tabel.
    mesin_kode = models.CharField("Mesin", max_length=30, db_index=True)
    tanggal = models.DateField("Tanggal")
    shift = models.CharField("Shift", max_length=1, choices=Shift.choices)
    jam_mulai = models.TimeField("Jam mulai")
    jam_selesai = models.TimeField("Jam selesai")
    nomor_produksi = models.CharField("Nomor produksi", max_length=100, blank=True)

    input = models.DecimalField("Input", max_digits=12, decimal_places=2, null=True, blank=True)
    output = models.DecimalField("Output", max_digits=12, decimal_places=2, null=True, blank=True)
    scrap = models.DecimalField("Scrap", max_digits=12, decimal_places=2, null=True, blank=True)
    defect_ng = models.DecimalField("Defect / NG", max_digits=12, decimal_places=2, null=True, blank=True)

    next_proses = models.CharField("Next process", max_length=150, blank=True)
    petugas = models.CharField("Petugas", max_length=150, help_text="Operator yang memantau mesin.")
    remark = models.TextField("Remark", blank=True)

    # Field khusus tiap jenis mesin (lihat JENIS_DETAIL_FIELDS).
    detail = models.JSONField("Detail mesin", default=dict, blank=True)

    dicatat_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="catatan_produksi", verbose_name="Dicatat oleh",
    )
    created_at = models.DateTimeField("Waktu input", auto_now_add=True)

    class Meta:
        verbose_name = "Catatan Produksi"
        verbose_name_plural = "Catatan Produksi"
        ordering = ["-tanggal", "-created_at"]

    def __str__(self):
        return f"{self.mesin_kode} · {self.tanggal} · Shift {self.shift}"

    @property
    def mesin(self):
        """Definisi mesin dari registry kode (atau None bila kodenya dihapus)."""
        return get_machine(self.mesin_kode)

    @property
    def durasi(self):
        """timedelta proses; menangani shift yang melewati tengah malam."""
        if not (self.jam_mulai and self.jam_selesai):
            return None
        start = datetime.combine(date.min, self.jam_mulai)
        end = datetime.combine(date.min, self.jam_selesai)
        if end < start:
            end += timedelta(days=1)
        return end - start

    @property
    def durasi_display(self):
        td = self.durasi
        if td is None:
            return "-"
        total_min = int(td.total_seconds() // 60)
        h, m = divmod(total_min, 60)
        return f"{h}j {m}m"

    def detail_display(self):
        """[(label, nilai), ...] untuk field khusus, sesuai jenis mesinnya."""
        mesin = self.mesin
        if mesin is None:
            return []
        labels = {key: label for key, label, _ in JENIS_DETAIL_FIELDS.get(mesin.jenis, [])}
        return [(labels.get(key, key), value) for key, value in (self.detail or {}).items()]
