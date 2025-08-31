#!/bin/bash
set -e

# Baserow Expansion Deployment Script
# Handles deployment with zero-downtime and rollback capabilities

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Configuration
ENVIRONMENT=${1:-production}
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.expansion.yml"
ENV_FILE="${SCRIPT_DIR}/.env.${ENVIRONMENT}"
BACKUP_BEFORE_DEPLOY=${BACKUP_BEFORE_DEPLOY:-true}
HEALTH_CHECK_TIMEOUT=${HEALTH_CHECK_TIMEOUT:-300}

echo "Starting Baserow Expansion deployment for environment: ${ENVIRONMENT}"

# Check if environment file exists
if [ ! -f "${ENV_FILE}" ]; then
    echo "Error: Environment file not found: ${ENV_FILE}"
    exit 1
fi

# Load environment variables
set -a
source "${ENV_FILE}"
set +a

# Function to check service health
check_health() {
    local service_url="http://localhost:8000/api/health/"
    local timeout=$1
    local elapsed=0
    
    echo "Checking service health..."
    while [ $elapsed -lt $timeout ]; do
        if curl -f -s "$service_url" > /dev/null; then
            echo "Service is healthy"
            return 0
        fi
        
        echo "Waiting for service to be healthy... (${elapsed}s/${timeout}s)"
        sleep 10
        elapsed=$((elapsed + 10))
    done
    
    echo "Health check failed after ${timeout} seconds"
    return 1
}

# Function to rollback deployment
rollback() {
    echo "Rolling back deployment..."
    
    # Stop new containers
    docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" down
    
    # Start previous version (if backup exists)
    if [ -f "${SCRIPT_DIR}/docker-compose.backup.yml" ]; then
        docker-compose -f "${SCRIPT_DIR}/docker-compose.backup.yml" up -d
        echo "Rollback completed"
    else
        echo "No backup configuration found for rollback"
    fi
    
    exit 1
}

# Trap to handle rollback on failure
trap rollback ERR

# 1. Pre-deployment backup
if [ "$BACKUP_BEFORE_DEPLOY" = "true" ]; then
    echo "Creating pre-deployment backup..."
    if [ -f "${SCRIPT_DIR}/scripts/backup.sh" ]; then
        bash "${SCRIPT_DIR}/scripts/backup.sh"
    else
        echo "Warning: Backup script not found, skipping backup"
    fi
fi

# 2. Build new images
echo "Building Docker images..."
cd "${PROJECT_ROOT}"
docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" build --no-cache

# 3. Backup current configuration
if docker-compose -f "${COMPOSE_FILE}" ps -q > /dev/null 2>&1; then
    echo "Backing up current configuration..."
    cp "${COMPOSE_FILE}" "${SCRIPT_DIR}/docker-compose.backup.yml"
fi

# 4. Run database migrations
echo "Running database migrations..."
docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" run --rm baserow-expansion python manage.py migrate

# 5. Initialize feature flags
echo "Initializing feature flags..."
docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" run --rm baserow-expansion python manage.py initialize_feature_flags

# 6. Collect static files (if needed)
echo "Collecting static files..."
docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" run --rm baserow-expansion python manage.py collectstatic --noinput

# 7. Start new services
echo "Starting new services..."
docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d

# 8. Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# 9. Health check
if ! check_health $HEALTH_CHECK_TIMEOUT; then
    echo "Deployment failed health check"
    rollback
fi

# 10. Run post-deployment tests
echo "Running post-deployment tests..."
if [ -f "${SCRIPT_DIR}/scripts/post-deploy-tests.sh" ]; then
    bash "${SCRIPT_DIR}/scripts/post-deploy-tests.sh"
else
    echo "No post-deployment tests found, skipping"
fi

# 11. Cleanup old images
echo "Cleaning up old Docker images..."
docker image prune -f

# 12. Send deployment notification
if [ -n "${DEPLOYMENT_WEBHOOK_URL}" ]; then
    curl -X POST "${DEPLOYMENT_WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -d "{\"status\":\"success\",\"environment\":\"${ENVIRONMENT}\",\"timestamp\":\"$(date -Iseconds)\"}" \
        2>/dev/null || echo "Failed to send deployment notification"
fi

echo "Deployment completed successfully!"
echo ""
echo "Services status:"
docker-compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" ps

echo ""
echo "Access points:"
echo "- Application: ${BASEROW_PUBLIC_URL}"
echo "- Grafana: http://localhost:3000 (admin/${GRAFANA_PASSWORD})"
echo "- Prometheus: http://localhost:9090"
echo "- Alertmanager: http://localhost:9093"

# Remove trap
trap - ERR