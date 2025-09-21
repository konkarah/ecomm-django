#!/bin/bash

echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database started"

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"