#!/bin/bash
set -e

echo "Environment: ${ENVIRONMENT:-dev}"
echo "Running migrations..."
python manage.py migrate --noinput

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "Starting server..."
if [ "$DEBUG" = "True" ]; then
    python manage.py runserver 0.0.0.0:8000
else
    # Use gunicorn for production
    gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4
fi