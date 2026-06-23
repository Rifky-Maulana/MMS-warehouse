from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, Division, Location, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Organisasi", {"fields": ("division", "location")}),
    )
    list_display = ("username", "email", "location", "division", "is_staff", "is_active")
    list_filter = BaseUserAdmin.list_filter + ("location", "division")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "description", "created_at")
    list_filter = ("action",)
    search_fields = ("description", "action")
    readonly_fields = ("user", "action", "description", "ip_address", "created_at")

    def has_add_permission(self, request):
        return False
