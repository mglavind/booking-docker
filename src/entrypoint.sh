#!/bin/bash
set -e

echo "Environment: ${ENVIRONMENT:-dev}"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "staging" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "Starting server..."
if [ "$DEBUG" = "True" ]; then
    python manage.py runserver 0.0.0.0:8000
else
    # UPDATED: Added logging flags to catch the 500 error traceback
    exec gunicorn core.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --log-level debug \
        --access-logfile - \
        --error-logfile - \
        --capture-output
fi