#!/bin/bash
set -e

# Baserow Expansion Backup Script
# Creates comprehensive backups of database, files, and configuration

BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="baserow_expansion_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Configuration
DATABASE_HOST=${DATABASE_HOST:-postgres}
DATABASE_PORT=${DATABASE_PORT:-5432}
DATABASE_NAME=${DATABASE_NAME:-baserow}
DATABASE_USER=${DATABASE_USER:-baserow}
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

echo "Starting Baserow Expansion backup: ${BACKUP_NAME}"

# Create backup directory
mkdir -p "${BACKUP_PATH}"

# 1. Database backup
echo "Backing up PostgreSQL database..."
pg_dump -h "${DATABASE_HOST}" -p "${DATABASE_PORT}" -U "${DATABASE_USER}" -d "${DATABASE_NAME}" \
    --verbose --clean --if-exists --create \
    --format=custom \
    --file="${BACKUP_PATH}/database.dump"

# Also create a plain SQL backup for easier restoration
pg_dump -h "${DATABASE_HOST}" -p "${DATABASE_PORT}" -U "${DATABASE_USER}" -d "${DATABASE_NAME}" \
    --verbose --clean --if-exists --create \
    --format=plain \
    --file="${BACKUP_PATH}/database.sql"

echo "Database backup completed"

# 2. Redis backup
echo "Backing up Redis data..."
redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" --rdb "${BACKUP_PATH}/redis.rdb"
echo "Redis backup completed"

# 3. File storage backup
echo "Backing up file storage..."
if [ -d "/baserow/data" ]; then
    tar -czf "${BACKUP_PATH}/files.tar.gz" -C /baserow data/
    echo "File storage backup completed"
else
    echo "No file storage directory found, skipping"
fi

# 4. Configuration backup
echo "Backing up configuration..."
mkdir -p "${BACKUP_PATH}/config"

# Copy environment variables
env | grep -E '^(BASEROW|DATABASE|REDIS|FEATURE|MONITORING)' > "${BACKUP_PATH}/config/environment.txt"

# Copy configuration files
if [ -d "/baserow/config" ]; then
    cp -r /baserow/config/* "${BACKUP_PATH}/config/"
fi

# Copy feature flags
if command -v python &> /dev/null; then
    python -c "
import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baserow.config.settings.base')
django.setup()
from baserow.contrib.database.expansion.feature_flags import FeatureFlag
flags = list(FeatureFlag.objects.values())
with open('${BACKUP_PATH}/config/feature_flags.json', 'w') as f:
    json.dump(flags, f, indent=2, default=str)
print('Feature flags exported')
" 2>/dev/null || echo "Could not export feature flags"
fi

echo "Configuration backup completed"

# 5. Create backup metadata
cat > "${BACKUP_PATH}/metadata.json" << EOF
{
    "backup_name": "${BACKUP_NAME}",
    "timestamp": "${TIMESTAMP}",
    "version": "$(python -c 'import baserow; print(baserow.__version__)' 2>/dev/null || echo 'unknown')",
    "database_host": "${DATABASE_HOST}",
    "database_name": "${DATABASE_NAME}",
    "redis_host": "${REDIS_HOST}",
    "backup_type": "full",
    "components": [
        "database",
        "redis",
        "files",
        "configuration"
    ]
}
EOF

# 6. Create compressed archive
echo "Creating compressed archive..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}/"
rm -rf "${BACKUP_NAME}/"

echo "Backup archive created: ${BACKUP_NAME}.tar.gz"

# 7. Cleanup old backups
echo "Cleaning up old backups (keeping ${RETENTION_DAYS} days)..."
find "${BACKUP_DIR}" -name "baserow_expansion_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete

# 8. Verify backup
echo "Verifying backup archive..."
if tar -tzf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" > /dev/null; then
    echo "Backup verification successful"
    
    # Calculate backup size
    BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
    echo "Backup size: ${BACKUP_SIZE}"
    
    # Send notification if webhook is configured
    if [ -n "${BACKUP_WEBHOOK_URL}" ]; then
        curl -X POST "${BACKUP_WEBHOOK_URL}" \
            -H "Content-Type: application/json" \
            -d "{\"status\":\"success\",\"backup_name\":\"${BACKUP_NAME}\",\"size\":\"${BACKUP_SIZE}\"}" \
            2>/dev/null || echo "Failed to send backup notification"
    fi
    
    echo "Backup completed successfully: ${BACKUP_NAME}.tar.gz"
    exit 0
else
    echo "Backup verification failed!"
    
    # Send failure notification
    if [ -n "${BACKUP_WEBHOOK_URL}" ]; then
        curl -X POST "${BACKUP_WEBHOOK_URL}" \
            -H "Content-Type: application/json" \
            -d "{\"status\":\"failed\",\"backup_name\":\"${BACKUP_NAME}\",\"error\":\"verification_failed\"}" \
            2>/dev/null || echo "Failed to send backup failure notification"
    fi
    
    exit 1
fi