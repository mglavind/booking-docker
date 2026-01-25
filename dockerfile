FROM python:3.13-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
WORKDIR /app

# 1. Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup uv and non-root user
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN useradd -m django-user

# 3. Prepare static volume with correct permissions
# We do this as root so we can create folders in /vol
RUN mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

# 4. Install requirements
COPY src/requirements.txt /app/requirements.txt
RUN uv pip install --system -r /app/requirements.txt

# 5. Copy source code and fix ownership
COPY --chown=django-user:django-user src/ /app/

# Switch to the non-root user for security
USER django-user

# 6. Bake static files into the image
# This requires ENVIRONMENT=production or staging to be passed
# or for your settings.py to handle a dummy SECRET_KEY if missing.
RUN python manage.py collectstatic --noinput

RUN chmod +x /app/entrypoint.sh
EXPOSE 8000 

CMD ["./entrypoint.sh"]