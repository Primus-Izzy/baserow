#!/bin/bash
set -e

# Baserow Expansion Restore Script
# Restores from backup created by backup.sh

BACKUP_DIR="/backups"
DATABASE_HOST=${DATABASE_HOST:-postgres}
DATABASE_PORT=${DATABASE_PORT:-5432}
DATABASE_NAME=${DATABASE_NAME:-baserow}
DATABASE_USER=${DATABASE_USER:-baserow}
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}

# Function to show usage
show_usage() {
    echo "Usage: $0 <backup_name>"
    echo "Example: $0 baserow_expansion_20240131_120000"
    echo ""
    echo "Available backups:"
    ls -la "${BACKUP_DIR}"/baserow_expansion_*.tar.gz 2>/dev/null | awk '{print $9}' | sed 's/.*\///' | sed 's/\.tar\.gz$//' || echo "No backups found"
}

# Check if backup name is provided
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

BACKUP_NAME="$1"
BACKUP_ARCHIVE="${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
RESTORE_DIR="${BACKUP_DIR}/restore_${BACKUP_NAME}"

# Check if backup exists
if [ ! -f "${BACKUP_ARCHIVE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_ARCHIVE}"
    show_usage
    exit 1
fi

echo "Starting restore from backup: ${BACKUP_NAME}"

# Confirmation prompt
read -p "This will overwrite existing data. Are you sure? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

# Extract backup
echo "Extracting backup archive..."
mkdir -p "${RESTORE_DIR}"
tar -xzf "${BACKUP_ARCHIVE}" -C "${RESTORE_DIR}" --strip-components=1

# Verify backup contents
if [ ! -f "${RESTORE_DIR}/metadata.json" ]; then
    echo "Error: Invalid backup - metadata.json not found"
    exit 1
fi

echo "Backup metadata:"
cat "${RESTORE_DIR}/metadata.json"
echo ""

# Stop services (if running in the same container)
echo "Stopping services..."
pkill -f "celery" || true
pkill -f "gunicorn" || true

# 1. Restore database
if [ -f "${RESTORE_DIR}/database.dump" ]; then
    echo "Restoring PostgreSQL database..."
    
    # Drop existing database (be careful!)
    dropdb -h "${DATABASE_HOST}" -p "${DATABASE_PORT}" -U "${DATABASE_USER}" "${DATABASE_NAME}" --if-exists
    
    # Restore from custom format
    pg_restore -h "${DATABASE_HOST}" -p "${DATABASE_PORT}" -U "${DATABASE_USER}" \
        --create --clean --if-exists \
        --dbname=postgres \
        "${RESTORE_DIR}/database.dump"
    
    echo "Database restore completed"
else
    echo "Warning: No database backup found"
fi

# 2. Restore Redis
if [ -f "${RESTORE_DIR}/redis.rdb" ]; then
    echo "Restoring Redis data..."
    
    # Stop Redis temporarily
    redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" SHUTDOWN NOSAVE || true
    sleep 2
    
    # Copy RDB file (this would need to be done differently in production)
    echo "Note: Redis restore requires manual intervention in production"
    echo "Copy ${RESTORE_DIR}/redis.rdb to Redis data directory and restart Redis"
else
    echo "Warning: No Redis backup found"
fi

# 3. Restore files
if [ -f "${RESTORE_DIR}/files.tar.gz" ]; then
    echo "Restoring file storage..."
    
    # Backup existing files
    if [ -d "/baserow/data" ]; then
        mv /baserow/data "/baserow/data.backup.$(date +%s)"
    fi
    
    # Extract files
    tar -xzf "${RESTORE_DIR}/files.tar.gz" -C /baserow/
    
    echo "File storage restore completed"
else
    echo "Warning: No file storage backup found"
fi

# 4. Restore configuration
if [ -d "${RESTORE_DIR}/config" ]; then
    echo "Restoring configuration..."
    
    # Restore feature flags
    if [ -f "${RESTORE_DIR}/config/feature_flags.json" ]; then
        python -c "
import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baserow.config.settings.base')
django.setup()
from baserow.contrib.database.expansion.feature_flags import FeatureFlag

with open('${RESTORE_DIR}/config/feature_flags.json', 'r') as f:
    flags = json.load(f)

for flag_data in flags:
    flag_data.pop('id', None)  # Remove ID to avoid conflicts
    flag_data.pop('created_at', None)
    flag_data.pop('updated_at', None)
    
    FeatureFlag.objects.update_or_create(
        name=flag_data['name'],
        defaults=flag_data
    )

print('Feature flags restored')
" 2>/dev/null || echo "Could not restore feature flags"
    fi
    
    echo "Configuration restore completed"
else
    echo "Warning: No configuration backup found"
fi

# 5. Run migrations to ensure database is up to date
echo "Running database migrations..."
python manage.py migrate

# 6. Clear caches
echo "Clearing caches..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baserow.config.settings.base')
django.setup()
from django.core.cache import cache
cache.clear()
print('Cache cleared')
" 2>/dev/null || echo "Could not clear cache"

# 7. Cleanup
echo "Cleaning up temporary files..."
rm -rf "${RESTORE_DIR}"

echo "Restore completed successfully!"
echo ""
echo "Next steps:"
echo "1. Restart all services"
echo "2. Verify data integrity"
echo "3. Test critical functionality"
echo "4. Monitor logs for any issues"

# Send notification if webhook is configured
if [ -n "${BACKUP_WEBHOOK_URL}" ]; then
    curl -X POST "${BACKUP_WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -d "{\"status\":\"restore_completed\",\"backup_name\":\"${BACKUP_NAME}\"}" \
        2>/dev/null || echo "Failed to send restore notification"
fi