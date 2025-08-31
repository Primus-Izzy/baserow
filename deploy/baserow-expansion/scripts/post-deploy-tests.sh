#!/bin/bash
set -e

# Post-deployment tests for Baserow Expansion
# Verifies that all critical functionality is working after deployment

BASE_URL=${BASEROW_PUBLIC_URL:-http://localhost:8000}
API_URL="${BASE_URL}/api"

echo "Running post-deployment tests..."

# Function to make API requests
api_request() {
    local method=$1
    local endpoint=$2
    local data=${3:-}
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "${API_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "${API_URL}${endpoint}"
    fi
}

# Test 1: Health check
echo "Testing health endpoint..."
health_response=$(curl -s -w "%{http_code}" "${API_URL}/health/")
if [[ "$health_response" == *"200" ]]; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    exit 1
fi

# Test 2: Metrics endpoint
echo "Testing metrics endpoint..."
metrics_response=$(curl -s -w "%{http_code}" "${API_URL}/metrics/")
if [[ "$metrics_response" == *"200" ]]; then
    echo "✓ Metrics endpoint accessible"
else
    echo "✗ Metrics endpoint failed"
    exit 1
fi

# Test 3: Database connectivity
echo "Testing database connectivity..."
db_test=$(python3 -c "
import os
import django
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baserow.config.settings.base')
django.setup()
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1;')
        result = cursor.fetchone()
    print('Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
" 2>&1)

if [[ $? -eq 0 ]]; then
    echo "✓ Database connectivity test passed"
else
    echo "✗ Database connectivity test failed: $db_test"
    exit 1
fi

# Test 4: Redis connectivity
echo "Testing Redis connectivity..."
redis_test=$(redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping 2>&1)
if [[ "$redis_test" == "PONG" ]]; then
    echo "✓ Redis connectivity test passed"
else
    echo "✗ Redis connectivity test failed: $redis_test"
    exit 1
fi

# Test 5: Feature flags
echo "Testing feature flags..."
feature_flags_test=$(python3 -c "
import os
import django
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baserow.config.settings.base')
django.setup()
try:
    from baserow.contrib.database.expansion.feature_flags import FeatureFlagManager
    flags = FeatureFlagManager.get_enabled_flags()
    print(f'Feature flags loaded: {len(flags)} flags')
    sys.exit(0)
except Exception as e:
    print(f'Feature flags test failed: {e}')
    sys.exit(1)
" 2>&1)

if [[ $? -eq 0 ]]; then
    echo "✓ Feature flags test passed"
else
    echo "✗ Feature flags test failed: $feature_flags_test"
    exit 1
fi

# Test 6: Celery workers
echo "Testing Celery workers..."
celery_test=$(celery -A baserow inspect ping 2>&1)
if [[ "$celery_test" == *"pong"* ]]; then
    echo "✓ Celery workers test passed"
else
    echo "⚠ Celery workers test failed (non-critical): $celery_test"
fi

# Test 7: Static files
echo "Testing static files..."
static_response=$(curl -s -w "%{http_code}" "${BASE_URL}/static/img/logo.svg")
if [[ "$static_response" == *"200" ]]; then
    echo "✓ Static files test passed"
else
    echo "⚠ Static files test failed (non-critical)"
fi

# Test 8: WebSocket connectivity (if available)
echo "Testing WebSocket connectivity..."
# This would require a more complex test with a WebSocket client
echo "⚠ WebSocket test skipped (requires manual verification)"

# Test 9: Monitoring services
echo "Testing monitoring services..."

# Prometheus
prometheus_response=$(curl -s -w "%{http_code}" "http://localhost:9090/-/healthy" 2>/dev/null || echo "000")
if [[ "$prometheus_response" == *"200" ]]; then
    echo "✓ Prometheus is healthy"
else
    echo "⚠ Prometheus health check failed (non-critical)"
fi

# Grafana
grafana_response=$(curl -s -w "%{http_code}" "http://localhost:3000/api/health" 2>/dev/null || echo "000")
if [[ "$grafana_response" == *"200" ]]; then
    echo "✓ Grafana is healthy"
else
    echo "⚠ Grafana health check failed (non-critical)"
fi

# Test 10: Performance test
echo "Running basic performance test..."
start_time=$(date +%s%N)
for i in {1..10}; do
    curl -s "${API_URL}/health/" > /dev/null
done
end_time=$(date +%s%N)
duration=$(( (end_time - start_time) / 1000000 ))
avg_response_time=$(( duration / 10 ))

echo "Average response time: ${avg_response_time}ms"
if [ $avg_response_time -lt 1000 ]; then
    echo "✓ Performance test passed"
else
    echo "⚠ Performance test warning: slow response times"
fi

echo ""
echo "Post-deployment tests completed!"
echo "Summary:"
echo "- All critical tests passed ✓"
echo "- Some non-critical tests may have warnings ⚠"
echo ""
echo "Manual verification recommended for:"
echo "- User authentication and authorization"
echo "- View types (Kanban, Timeline, Calendar)"
echo "- Real-time collaboration features"
echo "- Email notifications"
echo "- External integrations"