from django.contrib.auth.models import AbstractUser
from django.db import models


class Division(models.Model):
    """Divisi perusahaan (Gudang, dan nanti bisa SDM, Keuangan, dst)."""
    name = models.CharField("Nama", max_length=100)
    code = models.CharField("Kode", max_length=20, unique=True)  # mis. "WH"

    class Meta:
        verbose_name = "Divisi"
        verbose_name_plural = "Divisi"

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    User aplikasi. AbstractUser sudah menyediakan username, email,
    password, is_active, is_staff, grup & izin. Kita hanya menambah divisi.
    """
    division = models.ForeignKey(
        Division,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="Divisi",
    )

    def __str__(self):
        return self.get_full_name() or self.username


class AuditLog(models.Model):
    """Jejak aktivitas penting: siapa, apa, kapan, dari IP mana."""
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
        verbose_name="Pelaku",
    )
    action = models.CharField("Aksi", max_length=100)            # mis. "stock.out"
    description = models.CharField("Keterangan", max_length=255, blank=True)
    ip_address = models.GenericIPAddressField("Alamat IP", null=True, blank=True)
    created_at = models.DateTimeField("Waktu", auto_now_add=True)

    class Meta:
        verbose_name = "Catatan Audit"
        verbose_name_plural = "Catatan Audit"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} — {self.created_at:%Y-%m-%d %H:%M}"
