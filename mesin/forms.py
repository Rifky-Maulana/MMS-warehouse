from decimal import Decimal

from django import forms

from .models import (
    JENIS_COMMON_FIELDS,
    JENIS_DETAIL_FIELDS,
    CatatanProduksi,
)

LULUS_CHOICES = [("", "—"), ("lulus", "Lulus"), ("gagal", "Gagal")]

# Field umum yang selalu tampil di semua jenis mesin.
_ALWAYS = ("tanggal", "shift", "jam_mulai", "jam_selesai", "nomor_produksi",
           "next_proses", "petugas", "remark")
# Field umum yang tampilnya tergantung jenis mesin.
_VARIABLE = ("input", "output", "scrap", "defect_ng")


class CatatanProduksiForm(forms.ModelForm):
    class Meta:
        model = CatatanProduksi
        fields = (
            "tanggal", "shift", "jam_mulai", "jam_selesai", "nomor_produksi",
            "input", "output", "scrap", "defect_ng",
            "next_proses", "petugas", "remark",
        )
        widgets = {
            "tanggal": forms.DateInput(attrs={"type": "date"}),
            "jam_mulai": forms.TimeInput(attrs={"type": "time"}),
            "jam_selesai": forms.TimeInput(attrs={"type": "time"}),
            "remark": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, mesin=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesin = mesin
        jenis = mesin.jenis if mesin else None
        show = JENIS_COMMON_FIELDS.get(jenis, {f: True for f in _VARIABLE})

        # Buang field umum-variabel yang tidak relevan untuk jenis ini.
        for name in _VARIABLE:
            if not show.get(name, True):
                self.fields.pop(name, None)

        # Label input/output mengikuti satuan mesin (pcs/kg/batch).
        unit = mesin.get_satuan_display() if mesin else ""
        if "input" in self.fields:
            self.fields["input"].label = f"Input ({unit})"
        if "output" in self.fields:
            self.fields["output"].label = f"Output ({unit})"

        # Tambah field khusus (akan disimpan ke kolom JSON `detail`).
        self.detail_field_names = []
        for name, label, ftype in JENIS_DETAIL_FIELDS.get(jenis, []):
            if ftype == "decimal":
                self.fields[name] = forms.DecimalField(
                    label=label, max_digits=12, decimal_places=2, required=False)
            elif ftype == "lulus":
                self.fields[name] = forms.ChoiceField(
                    label=label, choices=LULUS_CHOICES, required=False)
            else:
                self.fields[name] = forms.CharField(label=label, required=False)
            self.detail_field_names.append(name)

        # Field wajib diisi.
        for req in ("tanggal", "shift", "jam_mulai", "jam_selesai", "petugas"):
            if req in self.fields:
                self.fields[req].required = True
        if "output" in self.fields:
            self.fields["output"].required = True

        # Styling seragam dengan modul lain.
        css = "w-full bg-brand-soft rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-brand/30"
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", css)

        # Hook auto-hitung scrap: terisi otomatis (input − output) di browser,
        # tetap bisa diubah operator. Hanya untuk mesin yang punya input & output.
        if "scrap" in self.fields:
            self.fields["scrap"].help_text = "Terisi otomatis dari input − output; masih bisa diubah."

            def _tandai(name, extra):
                w = self.fields[name].widget
                w.attrs["class"] = (w.attrs.get("class", "") + " " + extra).strip()

            _tandai("scrap", "js-scrap")
            if "output" in self.fields:
                _tandai("output", "js-scrap-output")
            sumber = {"MIXING": ["pp_murni_kg", "bahan_daur_ulang_kg"],
                      "CRUSHING": ["input"]}.get(jenis, [])
            for name in sumber:
                if name in self.fields:
                    _tandai(name, "js-scrap-input")

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.mesin_kode = self.mesin.kode
        jenis = self.mesin.jenis
        show = JENIS_COMMON_FIELDS.get(jenis, {})

        # MIXING: input otomatis = PP murni + Bahan daur ulang.
        if jenis == "MIXING":
            pp = self.cleaned_data.get("pp_murni_kg") or Decimal("0")
            bd = self.cleaned_data.get("bahan_daur_ulang_kg") or Decimal("0")
            obj.input = pp + bd

        # Scrap otomatis = input − output bila field scrap tampil & dibiarkan kosong.
        if show.get("scrap") and obj.input is not None and obj.output is not None and obj.scrap is None:
            obj.scrap = obj.input - obj.output

        # Kumpulkan field khusus ke kolom JSON.
        detail = {}
        for name in self.detail_field_names:
            value = self.cleaned_data.get(name)
            if value in (None, ""):
                continue
            detail[name] = str(value) if isinstance(value, Decimal) else value
        obj.detail = detail

        if commit:
            obj.save()
        return obj
