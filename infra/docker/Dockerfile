# ---- base image ----
FROM python:3.11-slim

# ---- env & pip optimizations ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ---- system deps minimal ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git \
  && rm -rf /var/lib/apt/lists/*

# ---- workdir ----
WORKDIR /app

# ---- install python deps ----
# NOTE: file ini dicopy dari ROOT REPO karena build context = repo root
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# ---- copy source code ----
# Semua kode project disalin ke /app (root repo -> /app)
COPY . /app

# ---- expose port (sesuai settings.SERVER_PORT=8004) ----
EXPOSE 8004

# ---- default command ----
# Jika app kamu di app/main.py -> gunakan app.main:app
# Jika ternyata app-nya di app/utils/main.py, ganti ke: app.utils.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
