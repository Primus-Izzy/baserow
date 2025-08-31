"""
Django management command to initialize feature flags.
"""

from django.core.management.base import BaseCommand
from baserow.contrib.database.expansion.feature_flags import FeatureFlagManager


class Command(BaseCommand):
    help = 'Initialize default feature flags for Baserow expansion'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all feature flags to default values',
        )

    def handle(self, *args, **options):
        self.stdout.write('Initializing feature flags...')
        
        if options['reset']:
            self.stdout.write('Resetting all feature flags to defaults...')
            from baserow.contrib.database.expansion.feature_flags import FeatureFlag
            FeatureFlag.objects.all().delete()
        
        FeatureFlagManager.initialize_default_flags()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully initialized feature flags')
        )