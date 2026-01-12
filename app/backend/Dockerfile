FROM python:3.12-slim-bookworm

WORKDIR /app

# Toolchain mínimo para psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

ENV FLASK_APP=main.py
ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
