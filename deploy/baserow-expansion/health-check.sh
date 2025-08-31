#!/bin/bash
set -e

# Check if the main application is responding
if ! curl -f -s http://localhost:8000/api/health/ > /dev/null; then
    echo "Health check failed: Main application not responding"
    exit 1
fi

# Check database connection
if ! python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baserow.config.settings.base')
django.setup()
from django.db import connection
connection.ensure_connection()
print('Database connection OK')
"; then
    echo "Health check failed: Database connection failed"
    exit 1
fi

# Check Redis connection
if ! redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping > /dev/null; then
    echo "Health check failed: Redis connection failed"
    exit 1
fi

# Check Celery workers
if ! celery -A baserow inspect ping > /dev/null 2>&1; then
    echo "Warning: Celery workers not responding"
fi

echo "Health check passed"
exit 0