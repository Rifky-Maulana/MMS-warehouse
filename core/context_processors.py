from .access import can_access_production, can_access_warehouse


def modules(request):
    """Sediakan flag akses modul + daftar mesin ke semua template (untuk sidebar)."""
    user = request.user
    can_production = can_access_production(user)

    mesin_list = []
    if user.is_authenticated and can_production:
        from mesin.machines import all_machines
        mesin_list = all_machines()

    return {
        "can_warehouse": can_access_warehouse(user),
        "can_production": can_production,
        "mesin_list": mesin_list,
    }
