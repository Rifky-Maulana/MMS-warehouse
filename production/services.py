from django.core.exceptions import ValidationError
from django.db import transaction

from .models import ProductionItem, ProductionMovement


@transaction.atomic
def apply_production_movement(movement: ProductionMovement) -> ProductionMovement:
    """
    Terapkan satu transaksi stok Produksi dengan AMAN:
      - mengunci baris barang (select_for_update) agar tidak terjadi selisih
        saat dua orang input bersamaan,
      - memvalidasi stok (barang keluar tidak boleh melebihi stok yang ada),
      - memperbarui Stok Saat Ini, lalu menyimpan transaksinya.
    Semua dijalankan dalam satu database transaction (atomic): kalau ada yang
    gagal, semuanya dibatalkan — tidak ada perubahan setengah jadi.
    """
    # Kunci baris barang sampai transaksi ini selesai.
    item = ProductionItem.objects.select_for_update().get(pk=movement.item_id)

    if movement.type == ProductionMovement.Type.IN:
        item.current_stock += movement.quantity

    elif movement.type == ProductionMovement.Type.OUT:
        if movement.quantity > item.current_stock:
            raise ValidationError(
                f"Stok tidak cukup. Stok '{item.name}' saat ini "
                f"{item.current_stock}, diminta keluar {movement.quantity}."
            )
        item.current_stock -= movement.quantity

    elif movement.type == ProductionMovement.Type.ADJUSTMENT:
        # Penyesuaian: stok diset ke angka ini (hasil hitung fisik / stok opname).
        item.current_stock = movement.quantity

    else:
        raise ValidationError("Jenis transaksi tidak dikenal.")

    item.save(update_fields=["current_stock"])
    movement.save()
    return movement
