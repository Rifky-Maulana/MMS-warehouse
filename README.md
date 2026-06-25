# Panduan Setup — Gudang MMS (Django)

Ditulis untuk pemula. Ikuti langkah demi langkah, dari atas ke bawah.

> **Kabar baik:** kamu **tidak perlu memasang Python atau Django** di komputermu. Semuanya berjalan di dalam Docker. Kamu cukup memasang **dua aplikasi**.

---

## Bagian 1 — Pasang dua aplikasi ini (sekali saja)

1. **Docker Desktop** — ini "aplikasi Docker" yang kamu maksud. Ia yang menjalankan aplikasi + database di komputermu secara terisolasi dan rapi.
   - Unduh: https://www.docker.com/products/docker-desktop/
   - Pasang, lalu **buka aplikasinya** dan biarkan berjalan. Pastikan statusnya **running** (ikon Docker muncul di taskbar/menu bar). Semua langkah berikut butuh Docker Desktop dalam keadaan menyala.

2. **Visual Studio Code** — editor untuk membuka & menyunting file.
   - Unduh: https://code.visualstudio.com/

Sudah, tidak perlu yang lain.

---

## Bagian 2 — Siapkan folder proyek

1. Ekstrak isi paket ini ke sebuah folder, misalnya `gudang-mms`.
2. Buka folder itu di VS Code: menu **File → Open Folder** → pilih folder tadi.
3. Buka terminal di dalam VS Code: menu **Terminal → New Terminal**. Semua perintah di bawah dijalankan di terminal ini.

---

## Bagian 3 — Buat file konfigurasi `.env`

Di terminal, jalankan:

```bash
cp .env.example .env
```

> Pengguna Windows (PowerShell), gunakan: `copy .env.example .env`

Untuk tahap belajar, isi bawaannya sudah cukup. (Mengganti password & kunci rahasia untuk produksi dibahas di bagian akhir.)

---

## Bagian 4 — Nyalakan aplikasi

```bash
docker compose up --build
```

Perintah ini akan: membangun image (memasang Python + Django + dependency — hanya lama saat **pertama** kali), lalu menyalakan dua layanan: aplikasi Django dan database PostgreSQL.

Tunggu sampai muncul baris seperti:

```
Starting development server at http://0.0.0.0:8000/
```

**Biarkan terminal ini tetap berjalan.**

---

## Bagian 5 — Siapkan database & buat akun admin pertama

Buka terminal **kedua** (menu **Terminal → New Terminal** lagi), lalu jalankan tiga perintah ini berurutan:

```bash
# 1. Terapkan migrasi ke database (membuat semua tabel: User, Divisi, Lokasi,
#    Audit, Kategori, Supplier, Barang, Transaksi Stok). Berkas migrasinya
#    sudah disertakan di proyek, jadi langsung migrate saja.
docker compose exec web python manage.py migrate

# 2. Buat akun admin pertama (akan diminta username, email, password)
docker compose exec web python manage.py createsuperuser
```

> Kalau nanti kamu **mengubah model** (menambah/menghapus field), barulah jalankan `docker compose exec web python manage.py makemigrations` lebih dulu, lalu `migrate` lagi.

---

## Bagian 6 — Buka di browser 🎉

- **Panel admin:** http://localhost:8000/admin
  Masuk dengan akun yang baru kamu buat. Di sini kamu **sudah bisa** mengelola User, Divisi, dan Catatan Audit — gratis dari Django.
- **Halaman aplikasi:** http://localhost:8000/
  Akan diarahkan ke halaman login, lalu ke Dashboard.

Kalau kedua halaman ini terbuka, fondasi Django-mu sudah berjalan. Selamat! 🚀

---

## Penggunaan sehari-hari

- **Menyalakan:** `docker compose up` (tanpa `--build`, lebih cepat)
- **Mematikan:** tekan `Ctrl + C` di terminal pertama, lalu jalankan `docker compose down`
- Karena ini mode pengembangan, setiap kali kamu menyunting file Python, server otomatis memuat ulang — tidak perlu restart manual.

---

## Kalau ada masalah

- **"port is already allocated" / port 8000 dipakai aplikasi lain:** buka `docker-compose.yml`, ubah `"8000:8000"` menjadi `"8001:8000"`, simpan, lalu buka http://localhost:8001
- **Perintah `docker` tidak dikenali / error koneksi:** pastikan **Docker Desktop sudah dibuka** dan statusnya running.
- **Perubahan tidak muncul:** hentikan dengan `Ctrl + C`, lalu `docker compose up` lagi.

---

## Struktur proyek (sekilas)

```
gudang-mms/
├── config/            # pengaturan proyek Django (settings, urls, wsgi)
├── core/              # app "inti": User, Divisi, Lokasi, Audit, Dashboard, kontrol akses
│   ├── models.py      #   User (M2M ke Divisi & Lokasi), Division, Location, AuditLog
│   ├── access.py      #   aturan hak akses (siapa boleh buka Gudang & lokasi mana)
│   └── views.py       #   Dashboard + halaman "tidak ada akses"
├── warehouse/         # app gudang: master data + transaksi stok + analitik
│   ├── models.py      #   Category, Supplier, Item (stok min, SKU per-lokasi), StockMovement
│   ├── services.py    #   apply_movement(): logika stok yang aman (atomic + row lock)
│   ├── forms.py       #   form input transaksi
│   └── views.py       #   daftar barang, transaksi, input transaksi, analitik
├── templates/         # tampilan HTML (base, dashboard, login, halaman warehouse)
├── Dockerfile         # cara membangun image aplikasi
├── docker-compose.yml # definisi layanan web + database
├── requirements.txt   # daftar paket Python (dipasang otomatis)
└── .env               # konfigurasi & rahasia (jangan dibagikan)
```

> Di Django, tiap **aplikasi** (folder seperti `core` atau `warehouse`) adalah satu modul mandiri. Divisi lain tinggal menambah folder app baru — persis rencana modular kita.

---

## Sebelum produksi (untuk nanti / rekan DevOps)

1. **Ganti kunci rahasia.** Hasilkan kunci acak dengan:
   ```bash
   docker compose exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Tempel hasilnya ke `DJANGO_SECRET_KEY` di `.env`.
2. Set `DJANGO_DEBUG=false` dan isi `DJANGO_ALLOWED_HOSTS` dengan domain internal (mis. `gudang.perusahaan.local`).
3. Ganti semua password di `.env` dengan yang kuat.
4. Jalankan dengan server produksi (**gunicorn**) di belakang reverse proxy/HTTPS. Konfigurasi produksi ini akan kita siapkan terpisah saat mendekati deployment.

---

## Fitur yang sudah berjalan

Status terkini: aplikasi sudah jauh dari sekadar fondasi. Yang sudah ada:

**Master data & inti**
- **User** dengan relasi ke banyak **Divisi** dan banyak **Lokasi** (many-to-many).
- **Lokasi gudang** dan **Divisi** sebagai data acuan.
- **Catatan Audit** (AuditLog) untuk melacak aksi penting.

**Gudang (`warehouse`)**
- **Barang (Item):** SKU **unik per lokasi** (kode sama boleh dipakai di lokasi berbeda), kategori, satuan (pcs/box/kg/liter/pack), **stok saat ini**, **stok minimum**, dan status **aktif/nonaktif** (barang bisa disembunyikan tanpa menghapus riwayatnya).
- **Kategori** & **Supplier** sebagai master data pendukung.
- **Transaksi Stok (StockMovement):** jenis **Masuk / Keluar / Penyesuaian**, dengan supplier, catatan, dan nomor referensi.
- **Logika stok yang aman** (`warehouse/services.py`): setiap transaksi berjalan *atomic* dengan **penguncian baris** (`select_for_update`) supaya stok tidak meleset saat dua orang input bersamaan; stok keluar tak boleh melebihi stok yang ada; penyesuaian menyetel stok ke hasil hitung fisik.

**Halaman aplikasi (di luar panel admin)**
- **Dashboard** — ringkasan: total barang, jumlah stok menipis, total transaksi, daftar stok menipis, dan transaksi terbaru.
- **Daftar Barang** — pencarian (nama/SKU) + filter lokasi, kategori, "stok menipis", dan tampilkan barang nonaktif.
- **Daftar Transaksi** — filter jenis/lokasi/kategori + pencarian, dengan paginasi.
- **Input Transaksi** — form pencatatan stok masuk/keluar/penyesuaian.
- **Analitik** — total masuk/keluar, barang teratas (in/out), dan tren harian, bisa difilter rentang tanggal, kategori, pencatat, dan lokasi (khusus staf).

**Kontrol akses (`core/access.py`)**
- Superadmin melihat **semua lokasi**; user biasa hanya melihat data **lokasi yang ditugaskan** padanya.
- Akses modul Gudang dibatasi berdasarkan divisi (lihat `WAREHOUSE_DIVISION_CODE = "GUDANG"`).

## Langkah selanjutnya

Roadmap berikutnya akan menyempurnakan pelaporan, ekspor data, dan pengetatan hak akses per-peran. Detailnya menyusul seiring kebutuhan di lapangan.
