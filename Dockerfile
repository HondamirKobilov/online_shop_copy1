FROM python:3.12-slim

# Pillow uchun kutubxonalar
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# STATIC fayllarni yig‘ish
RUN python manage.py collectstatic --noinput

# Default command (runserver emas)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:9377"]
