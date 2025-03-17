#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Wait a moment to ensure all services are ready
echo "Waiting for services to be ready..."
sleep 2

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if DJANGO_SUPERUSER_* environment variables are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser already exists, skipping creation"
fi

# Update site configuration from markdown file
echo "Updating site configuration..."
python manage.py update_site_config

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server with 3 workers
echo "Starting Gunicorn server..."
gunicorn mickblog.wsgi:application --bind 0.0.0.0:8000 --workers 3 --reload