from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.paginator import Paginator
from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date

from core.access import allowed_locations, warehouse_required

from .forms import MovementForm
from .models import Category, Item, StockMovement
from .services import apply_movement


def _scope_items(request, qs):
    if request.user.is_superuser:
        return qs
    return qs.filter(location__in=request.user.locations.all())


def _scope_movements(request, qs):
    if request.user.is_superuser:
        return qs
    return qs.filter(item__location__in=request.user.locations.all())


@login_required
@warehouse_required
def item_list(request):
    q = request.GET.get("q", "").strip()
    only_low = request.GET.get("low") == "1"
    show_inactive = request.GET.get("nonaktif") == "1"
    sel_locs = request.GET.getlist("lokasi")
    sel_cats = request.GET.getlist("kategori")

    items = _scope_items(request, Item.objects.select_related("category", "location")).order_by("name")
    if not show_inactive:
        items = items.filter(is_active=True)
    if q:
        items = items.filter(Q(name__icontains=q) | Q(sku__icontains=q))
    if only_low:
        items = items.filter(current_stock__lte=F("min_stock"))
    if sel_locs:
        items = items.filter(location_id__in=sel_locs)
    if sel_cats:
        items = items.filter(category_id__in=sel_cats)

    return render(request, "warehouse/item_list.html", {
        "items": items, "q": q, "only_low": only_low, "show_inactive": show_inactive,
        "loc_options": allowed_locations(request.user),
        "cat_options": Category.objects.all(),
        "sel_locs": sel_locs, "sel_cats": sel_cats,
    })


@login_required
@warehouse_required
def movement_list(request):
    mtype = request.GET.get("type", "")
    q = request.GET.get("q", "").strip()
    sel_locs = request.GET.getlist("lokasi")
    sel_cats = request.GET.getlist("kategori")

    qs = _scope_movements(request, StockMovement.objects.select_related("item", "item__location", "user", "supplier")).order_by("-created_at")
    if mtype in ("in", "out", "adjustment"):
        qs = qs.filter(type=mtype)
    if q:
        qs = qs.filter(Q(item__name__icontains=q) | Q(item__sku__icontains=q) | Q(reference__icontains=q))
    if sel_locs:
        qs = qs.filter(item__location_id__in=sel_locs)
    if sel_cats:
        qs = qs.filter(item__category_id__in=sel_cats)

    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    return render(request, "warehouse/movement_list.html", {
        "page": page, "type": mtype, "q": q,
        "loc_options": allowed_locations(request.user),
        "cat_options": Category.objects.all(),
        "sel_locs": sel_locs, "sel_cats": sel_cats,
    })


@login_required
@warehouse_required
def movement_create(request):
    if request.method == "POST":
        form = MovementForm(request.POST, user=request.user)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.user = request.user
            try:
                apply_movement(movement)
            except DjangoValidationError as e:
                form.add_error(None, "; ".join(e.messages))
            else:
                messages.success(request, "Transaksi berhasil dicatat.")
                return redirect("warehouse:movement_create")
    else:
        form = MovementForm(user=request.user)
    return render(request, "warehouse/movement_form.html", {"form": form})


@user_passes_test(lambda u: u.is_staff, login_url="login")
@warehouse_required
def analytics(request):
    today = date.today()
    date_to = parse_date(request.GET.get("to", "")) or today
    date_from = parse_date(request.GET.get("from", "")) or (today - timedelta(days=30))
    sel_cat = request.GET.get("kategori") or ""
    sel_user = request.GET.get("pencatat") or ""
    sel_locs = request.GET.getlist("lokasi")

    base = _scope_movements(request, StockMovement.objects.filter(
        created_at__date__gte=date_from, created_at__date__lte=date_to))
    if sel_cat:
        base = base.filter(item__category_id=sel_cat)
    if sel_user:
        base = base.filter(user_id=sel_user)
    if sel_locs:
        base = base.filter(item__location_id__in=sel_locs)

    total_in = base.filter(type="in").aggregate(s=Sum("quantity"))["s"] or 0
    total_out = base.filter(type="out").aggregate(s=Sum("quantity"))["s"] or 0

    def top(t):
        rows = (base.filter(type=t).values("item__name")
                .annotate(total=Sum("quantity")).order_by("-total")[:10])
        return {"labels": [r["item__name"] for r in rows], "values": [r["total"] for r in rows]}

    trend_rows = (base.annotate(day=TruncDate("created_at")).values("day").annotate(
        masuk=Coalesce(Sum("quantity", filter=Q(type="in")), 0),
        keluar=Coalesce(Sum("quantity", filter=Q(type="out")), 0),
    ).order_by("day"))
    trend = {
        "labels": [r["day"].strftime("%d %b") for r in trend_rows],
        "masuk": [r["masuk"] for r in trend_rows],
        "keluar": [r["keluar"] for r in trend_rows],
    }

    scoped_all = _scope_movements(request, StockMovement.objects.all())
    User = get_user_model()
    pencatat_list = User.objects.filter(
        id__in=scoped_all.values_list("user_id", flat=True).distinct()
    ).order_by("username")

    return render(request, "warehouse/analytics.html", {
        "date_from": date_from, "date_to": date_to,
        "total_in": total_in, "total_out": total_out,
        "chart_data": {"keluar": top("out"), "masuk": top("in"), "trend": trend},
        "categories": Category.objects.all(),
        "pencatat_list": pencatat_list,
        "loc_options": allowed_locations(request.user),
        "sel_cat": sel_cat, "sel_user": sel_user, "sel_locs": sel_locs,
    })
