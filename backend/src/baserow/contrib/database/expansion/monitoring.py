"""
Monitoring and metrics collection for Baserow expansion features.
"""

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.db import connection
from django.core.cache import cache
import time
import json
import logging
from typing import Dict, Any, List
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('baserow_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('baserow_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('baserow_active_users', 'Number of active users')
DATABASE_CONNECTIONS = Gauge('baserow_database_connections', 'Number of database connections')
CACHE_HIT_RATE = Gauge('baserow_cache_hit_rate', 'Cache hit rate')
CELERY_QUEUE_LENGTH = Gauge('baserow_celery_queue_length', 'Celery queue length', ['queue'])

class MetricsCollector:
    """Collects various system metrics for monitoring."""
    
    @staticmethod
    def collect_database_metrics() -> Dict[str, Any]:
        """Collect database-related metrics."""    
    try:
            with connection.cursor() as cursor:
                # Get connection count
                cursor.execute("SELECT count(*) FROM pg_stat_activity;")
                connection_count = cursor.fetchone()[0]
                DATABASE_CONNECTIONS.set(connection_count)
                
                # Get database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()));
                """)
                db_size = cursor.fetchone()[0]
                
                # Get table sizes
                cursor.execute("""
                    SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
                    FROM pg_tables 
                    WHERE schemaname = 'public' 
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC 
                    LIMIT 10;
                """)
                table_sizes = cursor.fetchall()
                
                return {
                    'connection_count': connection_count,
                    'database_size': db_size,
                    'largest_tables': [
                        {'schema': row[0], 'table': row[1], 'size': row[2]}
                        for row in table_sizes
                    ]
                }
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            return {}
    
    @staticmethod
    def collect_cache_metrics() -> Dict[str, Any]:
        """Collect cache-related metrics."""
        try:
            # Get cache statistics (Redis)
            from django.core.cache import cache
            
            # This would need to be implemented based on your cache backend
            # For Redis, you could use redis-py to get INFO stats
            cache_info = {
                'hit_rate': 0.95,  # Placeholder
                'memory_usage': '50MB',  # Placeholder
                'connected_clients': 10  # Placeholder
            }
            
            CACHE_HIT_RATE.set(cache_info['hit_rate'])
            
            return cache_info
        except Exception as e:
            logger.error(f"Error collecting cache metrics: {e}")
            return {}
    
    @staticmethod
    def collect_application_metrics() -> Dict[str, Any]:
        """Collect application-specific metrics."""
        try:
            from django.contrib.auth import get_user_model
            from baserow.contrib.database.models import Table, Database
            
            User = get_user_model()
            
            # Count active users (logged in within last 24 hours)
            active_threshold = timezone.now() - timezone.timedelta(hours=24)
            active_users = User.objects.filter(last_login__gte=active_threshold).count()
            ACTIVE_USERS.set(active_users)
            
            # Count total resources
            total_users = User.objects.count()
            total_databases = Database.objects.count()
            total_tables = Table.objects.count()
            
            return {
                'active_users': active_users,
                'total_users': total_users,
                'total_databases': total_databases,
                'total_tables': total_tables
            }
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return {}
    
    @staticmethod
    def collect_celery_metrics() -> Dict[str, Any]:
        """Collect Celery task queue metrics."""
        try:
            from celery import current_app
            
            inspect = current_app.control.inspect()
            active_tasks = inspect.active()
            scheduled_tasks = inspect.scheduled()
            
            # Count tasks by queue
            queue_lengths = {}
            if active_tasks:
                for worker, tasks in active_tasks.items():
                    for task in tasks:
                        queue = task.get('delivery_info', {}).get('routing_key', 'default')
                        queue_lengths[queue] = queue_lengths.get(queue, 0) + 1
            
            # Update Prometheus metrics
            for queue, length in queue_lengths.items():
                CELERY_QUEUE_LENGTH.labels(queue=queue).set(length)
            
            return {
                'active_tasks': sum(len(tasks) for tasks in (active_tasks or {}).values()),
                'scheduled_tasks': sum(len(tasks) for tasks in (scheduled_tasks or {}).values()),
                'queue_lengths': queue_lengths
            }
        except Exception as e:
            logger.error(f"Error collecting Celery metrics: {e}")
            return {}


class HealthChecker:
    """Performs health checks for various system components."""
    
    @staticmethod
    def check_database() -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'timestamp': timezone.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    @staticmethod
    def check_cache() -> Dict[str, Any]:
        """Check cache connectivity."""
        try:
            start_time = time.time()
            test_key = f"health_check_{int(time.time())}"
            cache.set(test_key, 'test', 10)
            result = cache.get(test_key)
            cache.delete(test_key)
            
            response_time = time.time() - start_time
            
            if result == 'test':
                return {
                    'status': 'healthy',
                    'response_time': response_time,
                    'timestamp': timezone.now().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Cache read/write failed',
                    'timestamp': timezone.now().isoformat()
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    @staticmethod
    def check_celery() -> Dict[str, Any]:
        """Check Celery worker connectivity."""
        try:
            from celery import current_app
            
            start_time = time.time()
            inspect = current_app.control.inspect()
            stats = inspect.stats()
            response_time = time.time() - start_time
            
            if stats:
                return {
                    'status': 'healthy',
                    'workers': len(stats),
                    'response_time': response_time,
                    'timestamp': timezone.now().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'No Celery workers responding',
                    'timestamp': timezone.now().isoformat()
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    @classmethod
    def get_overall_health(cls) -> Dict[str, Any]:
        """Get overall system health status."""
        checks = {
            'database': cls.check_database(),
            'cache': cls.check_cache(),
            'celery': cls.check_celery()
        }
        
        # Determine overall status
        all_healthy = all(check['status'] == 'healthy' for check in checks.values())
        overall_status = 'healthy' if all_healthy else 'unhealthy'
        
        return {
            'status': overall_status,
            'timestamp': timezone.now().isoformat(),
            'checks': checks
        }


def metrics_view(request):
    """Django view to expose Prometheus metrics."""
    if not getattr(settings, 'MONITORING_ENABLED', True):
        return HttpResponse('Monitoring disabled', status=404)
    
    # Collect current metrics
    MetricsCollector.collect_database_metrics()
    MetricsCollector.collect_cache_metrics()
    MetricsCollector.collect_application_metrics()
    MetricsCollector.collect_celery_metrics()
    
    # Return Prometheus format
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)


def health_view(request):
    """Django view for health checks."""
    health_data = HealthChecker.get_overall_health()
    status_code = 200 if health_data['status'] == 'healthy' else 503
    
    return HttpResponse(
        json.dumps(health_data, indent=2),
        content_type='application/json',
        status=status_code
    )