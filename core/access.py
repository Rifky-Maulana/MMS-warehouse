from functools import wraps

from django.shortcuts import redirect

# Kode divisi yang boleh membuka modul Gudang.
WAREHOUSE_DIVISION_CODE = "GUDANG"


def can_access_warehouse(user) -> bool:
    """Boleh buka modul Gudang jika: superadmin, ATAU belum punya divisi
    (biar user lama tidak terkunci), ATAU divisinya berkode GUDANG."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    div = user.division
    return div is None or div.code == WAREHOUSE_DIVISION_CODE


def warehouse_required(view_func):
    """Pagari view modul Gudang. User tanpa akses diarahkan ke halaman netral."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_access_warehouse(request.user):
            return redirect("no_access")
        return view_func(request, *args, **kwargs)
    return _wrapped
