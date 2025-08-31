#!/bin/bash
set -e

echo "Starting Baserow Expansion..."

# Wait for database
echo "Waiting for database..."
until pg_isready -h ${DATABASE_HOST:-postgres} -p ${DATABASE_PORT:-5432} -U ${DATABASE_USER:-baserow}; do
    echo "Database is unavailable - sleeping"
    sleep 1
done
echo "Database is up!"

# Wait for Redis
echo "Waiting for Redis..."
until redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping; do
    echo "Redis is unavailable - sleeping"
    sleep 1
done
echo "Redis is up!"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@baserow.io', 'password')
    print('Superuser created')
else:
    print('Superuser already exists')
"

# Initialize feature flags
echo "Initializing feature flags..."
python manage.py initialize_feature_flags

# Start monitoring services
if [ "$MONITORING_ENABLED" = "true" ]; then
    echo "Starting monitoring services..."
    python manage.py start_monitoring &
fi

# Start Celery workers for automation
echo "Starting Celery workers..."
celery -A baserow worker --loglevel=info --concurrency=4 &

# Start Celery beat for scheduled tasks
echo "Starting Celery beat..."
celery -A baserow beat --loglevel=info &

# Start the main application
echo "Starting Baserow application..."
exec gunicorn baserow.config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class gevent \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --access-logfile - \
    --error-logfile -