from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    context = {
        # Placeholder — akan diisi data nyata pada Tahap 4 (transaksi):
        "low_stock_items": [],
        "recent_transactions": [],
    }
    return render(request, "dashboard.html", context)
