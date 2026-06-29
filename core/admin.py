from types import MethodType

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .audit import AuditedModelAdmin
from .models import AuditLog, Division, Location, User


@admin.register(User)
class UserAdmin(AuditedModelAdmin, BaseUserAdmin):
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
class LocationAdmin(AuditedModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Division)
class DivisionAdmin(AuditedModelAdmin):
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
admin.site.site_header = "Merapi Medika Solusindo — Panel Admin"
admin.site.site_title = "Merapi Medika Solusindo Admin"
admin.site.index_title = "Modul MMS ERP"


# ===== Urutan section di halaman index admin =====
# Section paling atas dulu; yang tidak terdaftar di bawah, mengikuti urutan default.
_APP_ORDER = ["warehouse", "production", "mesin", "auth", "core"]


def _ordered_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)

    def app_key(app):
        label = app["app_label"]
        return (_APP_ORDER.index(label) if label in _APP_ORDER else len(_APP_ORDER),
                app["name"].lower())

    app_list = sorted(app_dict.values(), key=app_key)
    for app in app_list:
        app["models"].sort(key=lambda m: m["name"])
    return app_list


admin.site.get_app_list = MethodType(_ordered_app_list, admin.site)
