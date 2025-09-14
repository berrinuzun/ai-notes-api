# Base image
FROM python:3.12-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları (opsiyonel, psycopg2 için gerekli olabilir)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Requirements yükle
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Kodları kopyala
COPY . /app

# Port aç
EXPOSE 8000

# Başlatma komutu (proje yapına göre)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
