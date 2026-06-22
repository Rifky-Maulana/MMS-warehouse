from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, Division, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Tambahkan kolom Divisi ke form & daftar user bawaan Django
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Divisi", {"fields": ("division",)}),
    )
    list_display = ("username", "email", "division", "is_staff", "is_active")
    list_filter = BaseUserAdmin.list_filter + ("division",)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "description", "created_at")
    list_filter = ("action",)
    search_fields = ("description", "action")
    # Catatan audit hanya untuk dibaca, tidak boleh diubah manual.
    readonly_fields = ("user", "action", "description", "ip_address", "created_at")

    def has_add_permission(self, request):
        return False
