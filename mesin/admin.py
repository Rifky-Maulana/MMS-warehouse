from django.contrib import admin

from .machines import get_machine
from .models import CatatanProduksi


@admin.register(CatatanProduksi)
class CatatanProduksiAdmin(admin.ModelAdmin):
    list_display = ("tanggal", "mesin_nama", "shift", "durasi_display", "input", "output",
                    "scrap", "defect_ng", "petugas", "dicatat_oleh")
    list_filter = ("mesin_kode", "shift", "tanggal")
    search_fields = ("mesin_kode", "nomor_produksi", "petugas", "remark")
    list_select_related = ("dicatat_oleh",)
    date_hierarchy = "tanggal"
    readonly_fields = ("created_at",)

    @admin.display(description="Mesin", ordering="mesin_kode")
    def mesin_nama(self, obj):
        m = get_machine(obj.mesin_kode)
        return m.nama if m else obj.mesin_kode

    @admin.display(description="Durasi")
    def durasi_display(self, obj):
        return obj.durasi_display

    def save_model(self, request, obj, form, change):
        if not change and not obj.dicatat_oleh_id:
            obj.dicatat_oleh = request.user
        super().save_model(request, obj, form, change)
