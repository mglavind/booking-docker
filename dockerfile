# -----------------------------
# Stage 1: build Python environment
# -----------------------------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for psycopg2 and Pillow)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Install dependencies first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Stage 2: copy code and run app
# -----------------------------
FROM base AS app

WORKDIR /code

# Copy only necessary parts (not .git, node_modules, etc.)
COPY . .

# Collect static files during build
RUN python bookingsystem/manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", "bookingsystem.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]