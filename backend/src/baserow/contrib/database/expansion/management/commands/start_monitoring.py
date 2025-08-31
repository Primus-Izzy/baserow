"""
Django management command to start monitoring services.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import threading
import time
import logging
from baserow.contrib.database.expansion.monitoring import MetricsCollector

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start monitoring and metrics collection services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Metrics collection interval in seconds (default: 30)',
        )
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run as daemon process',
        )

    def handle(self, *args, **options):
        if not getattr(settings, 'MONITORING_ENABLED', True):
            self.stdout.write('Monitoring is disabled')
            return

        interval = options['interval']
        daemon = options['daemon']

        self.stdout.write(f'Starting monitoring with {interval}s interval...')

        def collect_metrics():
            while True:
                try:
                    # Collect all metrics
                    MetricsCollector.collect_database_metrics()
                    MetricsCollector.collect_cache_metrics()
                    MetricsCollector.collect_application_metrics()
                    MetricsCollector.collect_celery_metrics()
                    
                    logger.info('Metrics collected successfully')
                except Exception as e:
                    logger.error(f'Error collecting metrics: {e}')
                
                time.sleep(interval)

        if daemon:
            # Run in background thread
            thread = threading.Thread(target=collect_metrics, daemon=True)
            thread.start()
            self.stdout.write('Monitoring started in background')
        else:
            # Run in foreground
            try:
                collect_metrics()
            except KeyboardInterrupt:
                self.stdout.write('Monitoring stopped')