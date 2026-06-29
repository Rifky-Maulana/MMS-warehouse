from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render

from core.access import production_required

from .forms import CatatanProduksiForm
from .machines import get_machine
from .models import CatatanProduksi


@login_required
@production_required
def machine_page(request, kode):
    mesin = get_machine(kode)
    if mesin is None:
        raise Http404("Mesin tidak ditemukan.")

    if request.method == "POST":
        form = CatatanProduksiForm(request.POST, mesin=mesin)
        if form.is_valid():
            catatan = form.save(commit=False)
            catatan.dicatat_oleh = request.user
            catatan.save()
            messages.success(request, "Catatan produksi berhasil disimpan.")
            return redirect("mesin:machine_page", kode=kode)
    else:
        form = CatatanProduksiForm(mesin=mesin)

    riwayat = CatatanProduksi.objects.filter(mesin_kode=kode).select_related("dicatat_oleh")
    page = Paginator(riwayat, 20).get_page(request.GET.get("page"))

    return render(request, "mesin/machine_page.html", {
        "mesin": mesin, "form": form, "page": page,
    })
