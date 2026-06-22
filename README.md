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
# 1. Buat berkas migrasi dari model kita (User, Divisi, Audit)
docker compose exec web python manage.py makemigrations

# 2. Terapkan ke database (membuat tabel-tabelnya)
docker compose exec web python manage.py migrate

# 3. Buat akun admin pertama (akan diminta username, email, password)
docker compose exec web python manage.py createsuperuser
```

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
├── config/            # pengaturan proyek Django
├── core/              # aplikasi "inti": User, Divisi, Audit, Dashboard
├── templates/         # tampilan HTML
├── Dockerfile         # cara membangun image aplikasi
├── docker-compose.yml # definisi layanan web + database
├── requirements.txt   # daftar paket Python (dipasang otomatis)
└── .env               # konfigurasi & rahasia (jangan dibagikan)
```

> Di Django, tiap **aplikasi** (folder seperti `core`) adalah satu modul mandiri. Modul gudang nanti menjadi folder `warehouse`, dan divisi lain tinggal menambah folder app baru — persis rencana modular kita.

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

## Langkah selanjutnya

Setelah fondasi ini berjalan di komputermu, kita lanjut **Tahap 3 — Master Data Gudang**: aplikasi `warehouse` berisi model **kategori, supplier, dan barang** (lengkap dengan **stok minimum**), beserta pengelolaannya lewat panel admin Django. Setelah itu Tahap 4 (transaksi & logika stok) yang akan menghidupkan kartu-kartu di Dashboard.
