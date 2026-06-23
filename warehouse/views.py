from datetime import date, timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import F, Q, Sum
from django.shortcuts import render
from django.utils.dateparse import parse_date

from .models import Item, StockMovement


def _scope_items(request, qs):
    """Saring barang ke lokasi user (superadmin lihat semua)."""
    if not request.user.is_superuser:
        qs = qs.filter(location=request.user.location)
    return qs


def _scope_movements(request, qs):
    if not request.user.is_superuser:
        qs = qs.filter(item__location=request.user.location)
    return qs


@login_required
def item_list(request):
    q = request.GET.get("q", "").strip()
    only_low = request.GET.get("low") == "1"
    items = _scope_items(request, Item.objects.select_related("category", "location")).order_by("name")
    if q:
        items = items.filter(Q(name__icontains=q) | Q(sku__icontains=q))
    if only_low:
        items = items.filter(current_stock__lte=F("min_stock"))
    return render(request, "warehouse/item_list.html", {"items": items, "q": q, "only_low": only_low})


@login_required
def movement_list(request):
    mtype = request.GET.get("type", "")
    q = request.GET.get("q", "").strip()
    qs = _scope_movements(request, StockMovement.objects.select_related("item", "user", "supplier")).order_by("-created_at")
    if mtype in ("in", "out", "adjustment"):
        qs = qs.filter(type=mtype)
    if q:
        qs = qs.filter(Q(item__name__icontains=q) | Q(item__sku__icontains=q) | Q(reference__icontains=q))
    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    return render(request, "warehouse/movement_list.html", {"page": page, "type": mtype, "q": q})


@user_passes_test(lambda u: u.is_staff, login_url="login")
def analytics(request):
    today = date.today()
    date_to = parse_date(request.GET.get("to", "")) or today
    date_from = parse_date(request.GET.get("from", "")) or (today - timedelta(days=30))

    base = _scope_movements(request, StockMovement.objects.filter(
        created_at__date__gte=date_from, created_at__date__lte=date_to
    ))
    total_in = base.filter(type="in").aggregate(s=Sum("quantity"))["s"] or 0
    total_out = base.filter(type="out").aggregate(s=Sum("quantity"))["s"] or 0

    def top(t):
        rows = (base.filter(type=t).values("item__name")
                .annotate(total=Sum("quantity")).order_by("-total")[:10])
        return {"labels": [r["item__name"] for r in rows], "values": [r["total"] for r in rows]}

    return render(request, "warehouse/analytics.html", {
        "date_from": date_from, "date_to": date_to,
        "total_in": total_in, "total_out": total_out,
        "chart_data": {"keluar": top("out"), "masuk": top("in")},
    })
