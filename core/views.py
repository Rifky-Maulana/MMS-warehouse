from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render

from warehouse.models import Item, StockMovement


@login_required
def dashboard(request):
    low_stock = Item.objects.filter(current_stock__lte=F("min_stock")).order_by("name")
    recent = StockMovement.objects.select_related("item", "user")[:8]
    return render(request, "dashboard.html", {
        "low_stock_items": low_stock,
        "recent_transactions": recent,
        "total_items": Item.objects.count(),
        "low_stock_count": low_stock.count(),
        "total_movements": StockMovement.objects.count(),
    })
