"""
Performance monitoring utilities for Baserow database operations.
"""
import time
import logging
from contextlib import contextmanager
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and log performance metrics for database operations."""
    
    def __init__(self):
        self.metrics = {}
    
    @contextmanager
    def measure(self, operation_name):
        """Context manager to measure operation duration."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_metric(operation_name, duration)
    
    def record_metric(self, operation_name, duration):
        """Record a performance metric."""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        
        self.metrics[operation_name].append(duration)
        
        # Log slow operations
        if duration > getattr(settings, 'SLOW_OPERATION_THRESHOLD', 1.0):
            logger.warning(f"Slow operation detected: {operation_name} took {duration:.2f}s")
        
        # Cache recent metrics for dashboard
        cache_key = f"performance_metric_{operation_name}"
        recent_metrics = cache.get(cache_key, [])
        recent_metrics.append({
            'timestamp': time.time(),
            'duration': duration
        })
        
        # Keep only last 100 metrics
        recent_metrics = recent_metrics[-100:]
        cache.set(cache_key, recent_metrics, timeout=3600)
    
    def get_average_duration(self, operation_name):
        """Get average duration for an operation."""
        if operation_name not in self.metrics:
            return 0
        
        durations = self.metrics[operation_name]
        return sum(durations) / len(durations)
    
    def get_duration(self, operation_name):
        """Get the last recorded duration for an operation."""
        if operation_name not in self.metrics or not self.metrics[operation_name]:
            return 0
        return self.metrics[operation_name][-1]


# Global performance monitor instance
performance_monitor = PerformanceMonitor()