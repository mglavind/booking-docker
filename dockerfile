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

# 3. Install requirements (Done before copying code to use Docker cache)
COPY src/requirements.txt /app/requirements.txt
RUN uv pip install --system -r /app/requirements.txt

# 4. Copy source code
COPY --chown=django-user:django-user src/ /app/

# 5. Prepare static/media folders and permissions
# We create these in /app to match your settings.py STATIC_ROOT = '/app/staticfiles'
RUN mkdir -p /app/staticfiles /app/media && \
    chmod +x /app/entrypoint.sh && \
    chown -R django-user:django-user /app/staticfiles /app/media

# 6. Switch to the non-root user
USER django-user

# 7. Final Prep
EXPOSE 8000 

# Use ENTRYPOINT so the script always runs, and CMD for default arguments
ENTRYPOINT ["/app/entrypoint.sh"]