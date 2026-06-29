"""Daftar mesin — DIDEFINISIKAN DEVELOPER DI SINI, bukan dari admin.

Mesin sudah fixed dari pabrik. Untuk menambah/mengubah mesin, edit list
`MACHINES` di bawah (butuh developer), bukan lewat panel admin. Operator
cukup membuka halaman mesin dan mengisi catatan.

Jenis mesin menentukan bentuk form & field khususnya — lihat
`JENIS_DETAIL_FIELDS` / `JENIS_COMMON_FIELDS` di models.py.
"""
from dataclasses import dataclass

JENIS_DISPLAY = {
    "MIXING": "Mixing",
    "CRUSHING": "Crushing",
    "INJECTION": "Injection",
    "COUNTING": "Counting",
    "STERILIZATION": "Sterilization",
}
SATUAN_DISPLAY = {"pcs": "Pcs", "kg": "Kg", "batch": "Batch"}


@dataclass(frozen=True)
class Machine:
    kode: str          # dipakai di URL & sidebar, mis. "fl270"
    nama: str
    jenis: str         # MIXING / CRUSHING / INJECTION / COUNTING / STERILIZATION
    satuan: str = "pcs"
    produk: str = ""
    target_per_shift: object = None
    urutan: int = 0

    def get_jenis_display(self):
        return JENIS_DISPLAY.get(self.jenis, self.jenis)

    def get_satuan_display(self):
        return SATUAN_DISPLAY.get(self.satuan, self.satuan)


# ===== Daftar mesin (urut sesuai alur produksi) =====
MACHINES = [
    Machine("mixer",       "Mixer",                      "MIXING",        "kg",    "Material campuran", urutan=1),
    Machine("crusher",     "Crusher",                    "CRUSHING",      "kg",    "Material hancuran", urutan=2),
    Machine("fl270",       "Injection FL270 (Barrel)",   "INJECTION",     "pcs",   "Barrel",            urutan=3),
    Machine("fl220",       "Injection FL220 (Plunger)",  "INJECTION",     "pcs",   "Plunger",           urutan=4),
    Machine("printing",    "Barrel Printing",            "COUNTING",      "pcs",   "Barrel (printed)",  urutan=5),
    Machine("assembly",    "Assembly",                   "COUNTING",      "pcs",   "Syringe",           urutan=6),
    Machine("blister",     "Blister Packing",            "COUNTING",      "pcs",   "Syringe (blister)", urutan=7),
    Machine("sterilisasi", "Sterilisasi (EtO)",          "STERILIZATION", "batch", "Syringe steril",    urutan=8),
]

_BY_KODE = {m.kode: m for m in MACHINES}


def all_machines():
    return MACHINES


def get_machine(kode):
    return _BY_KODE.get(kode)
