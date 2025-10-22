# Dockerfile

FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /app

# --- افزودن خط حیاتی برای نصب پیش‌نیازهای سیستمی (مثل libpq-dev برای psycopg2) ---
RUN apt-get update && apt-get install -y build-essential libpq-dev postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

# --- استفاده از legacy-resolver برای حل تضادهای وابستگی (مثل protobuf) ---
RUN pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt

COPY . /app/
EXPOSE 8000