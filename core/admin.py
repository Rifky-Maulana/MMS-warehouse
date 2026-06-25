from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, Division, Location, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Organisasi", {"fields": ("divisions", "locations")}),
    )
    filter_horizontal = ("groups", "user_permissions", "divisions", "locations")
    list_display = ("username", "email", "lokasi_list", "divisi_list", "is_staff", "is_active")
    list_filter = BaseUserAdmin.list_filter + ("locations", "divisions")

    @admin.display(description="Lokasi")
    def lokasi_list(self, obj):
        return ", ".join(l.name for l in obj.locations.all()) or "-"

    @admin.display(description="Divisi")
    def divisi_list(self, obj):
        return ", ".join(d.name for d in obj.divisions.all()) or "-"


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


# ===== Branding panel admin =====
admin.site.site_header = "Gudang MMS — Panel Admin"
admin.site.site_title = "Gudang MMS Admin"
admin.site.index_title = "Modul MMS ERP"
