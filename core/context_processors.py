from .access import can_access_production, can_access_warehouse


def modules(request):
    """Sediakan flag akses modul ke semua template (untuk sidebar)."""
    return {
        "can_warehouse": can_access_warehouse(request.user),
        "can_production": can_access_production(request.user),
    }
