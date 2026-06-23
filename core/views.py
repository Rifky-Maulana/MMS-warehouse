from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render

from warehouse.models import Item, StockMovement


@login_required
def dashboard(request):
    items = Item.objects.all()
    movements = StockMovement.objects.all()
    if not request.user.is_superuser:
        items = items.filter(location=request.user.location)
        movements = movements.filter(item__location=request.user.location)

    low_stock = items.filter(current_stock__lte=F("min_stock")).order_by("name")
    recent = movements.select_related("item", "user").order_by("-created_at")[:8]
    return render(request, "dashboard.html", {
        "low_stock_items": low_stock,
        "recent_transactions": recent,
        "total_items": items.count(),
        "low_stock_count": low_stock.count(),
        "total_movements": movements.count(),
    })
