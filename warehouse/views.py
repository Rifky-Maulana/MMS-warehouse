from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.shortcuts import render

from .models import Item


@login_required
def item_list(request):
    q = request.GET.get("q", "").strip()
    only_low = request.GET.get("low") == "1"

    items = Item.objects.select_related("category").order_by("name")
    if q:
        items = items.filter(Q(name__icontains=q) | Q(sku__icontains=q))
    if only_low:
        items = items.filter(current_stock__lte=F("min_stock"))

    return render(request, "warehouse/item_list.html", {
        "items": items,
        "q": q,
        "only_low": only_low,
    })
