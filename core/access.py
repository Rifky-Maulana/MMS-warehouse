from functools import wraps

from django.shortcuts import redirect

WAREHOUSE_DIVISION_CODE = "GUDANG"
PRODUCTION_DIVISION_CODE = "PRODUKSI"


def _can_access_module(user, division_code) -> bool:
    """Aturan akses modul yang dipakai bersama semua modul ber-divisi:
    boleh jika superadmin, ATAU belum punya divisi sama sekali,
    ATAU salah satu divisinya berkode sesuai modul."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if not user.divisions.exists():
        return True
    return user.divisions.filter(code=division_code).exists()


def can_access_warehouse(user) -> bool:
    """Boleh buka Gudang jika: superadmin, ATAU belum punya divisi,
    ATAU salah satu divisinya berkode GUDANG."""
    return _can_access_module(user, WAREHOUSE_DIVISION_CODE)


def can_access_production(user) -> bool:
    """Boleh buka Produksi jika: superadmin, ATAU belum punya divisi,
    ATAU salah satu divisinya berkode PRODUKSI."""
    return _can_access_module(user, PRODUCTION_DIVISION_CODE)


def allowed_locations(user):
    """Queryset lokasi yang boleh dilihat user. Superadmin = semua lokasi."""
    from .models import Location
    if user.is_superuser:
        return Location.objects.all()
    return user.locations.all()


def warehouse_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_access_warehouse(request.user):
            return redirect("no_access")
        return view_func(request, *args, **kwargs)
    return _wrapped


def production_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_access_production(request.user):
            return redirect("no_access")
        return view_func(request, *args, **kwargs)
    return _wrapped
