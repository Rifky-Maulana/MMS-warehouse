# Image aplikasi — berisi Python + Django + semua dependency.
FROM python:3.13-slim

# Setelan Python yang umum untuk container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Pasang dependency dulu (memanfaatkan cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi
COPY . .

EXPOSE 8000

# Perintah bawaan = server pengembangan.
# Untuk produksi diganti gunicorn (lihat README, bagian "Sebelum produksi").
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
