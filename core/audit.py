"""Penulisan Catatan Audit (AuditLog).

AuditLog ditulis OTOMATIS oleh sistem, bukan diketik manual. Modul ini
menyediakan:
  - get_client_ip(request)  : ambil IP pelaku (sadar reverse proxy).
  - log_action(...)         : tulis satu baris AuditLog.
  - AuditedModelAdmin       : mixin admin yang mencatat tambah/ubah/hapus
                              master data (dipakai admin Barang, Kategori,
                              Supplier, Pengguna, Divisi, Lokasi, dst).

Transaksi stok SENGAJA tidak dicatat di sini — tabel StockMovement /
ProductionMovement sudah menjadi riwayatnya sendiri.
"""
from django.contrib import admin


def get_client_ip(request):
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_action(request, action, description=""):
    """Tulis satu baris AuditLog. Aman dipanggil walau request/user kosong."""
    from .models import AuditLog

    user = getattr(request, "user", None) if request is not None else None
    if user is not None and not user.is_authenticated:
        user = None
    AuditLog.objects.create(
        user=user,
        action=action[:100],
        description=description[:255],
        ip_address=get_client_ip(request),
    )


class AuditedModelAdmin(admin.ModelAdmin):
    """Mixin: catat setiap tambah/ubah/hapus objek master data ke AuditLog.

    Memakai hook save_model/delete_model/delete_queryset (stabil lintas versi
    Django) sehingga selalu punya akses ke request.user + IP pelaku.
    """

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        verb = "Ubah" if change else "Tambah"
        log_action(request, f"{verb} {obj._meta.verbose_name}", str(obj))

    def delete_model(self, request, obj):
        verbose_name = obj._meta.verbose_name
        repr_ = str(obj)
        super().delete_model(request, obj)
        log_action(request, f"Hapus {verbose_name}", repr_)

    def delete_queryset(self, request, queryset):
        verbose_name = queryset.model._meta.verbose_name
        reprs = [str(o) for o in queryset]
        super().delete_queryset(request, queryset)
        for repr_ in reprs:
            log_action(request, f"Hapus {verbose_name}", repr_)
