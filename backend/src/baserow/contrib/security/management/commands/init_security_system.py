from django.core.management.base import BaseCommand
from django.conf import settings
from cryptography.fernet import Fernet
import os

from baserow.contrib.security.models import RateLimitRule


class Command(BaseCommand):
    help = 'Initialize security system with default settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-encryption-key',
            action='store_true',
            help='Generate and save encryption key',
        )
        parser.add_argument(
            '--create-rate-limits',
            action='store_true',
            help='Create default rate limit rules',
        )

    def handle(self, *args, **options):
        if options['create_encryption_key']:
            self.create_encryption_key()
        
        if options['create_rate_limits']:
            self.create_default_rate_limits()
        
        self.stdout.write(
            self.style.SUCCESS('Security system initialized successfully')
        )

    def create_encryption_key(self):
        """Generate and save encryption key."""
        key = Fernet.generate_key()
        
        # Save to environment file or settings
        env_file = os.path.join(settings.BASE_DIR, '.env')
        
        if os.path.exists(env_file):
            with open(env_file, 'a') as f:
                f.write(f'\nBASEROW_ENCRYPTION_KEY={key.decode()}\n')
            
            self.stdout.write(
                self.style.SUCCESS(f'Encryption key saved to {env_file}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Add this to your environment: BASEROW_ENCRYPTION_KEY={key.decode()}'
                )
            )

    def create_default_rate_limits(self):
        """Create default rate limit rules."""
        default_rules = [
            {
                'name': 'API General',
                'endpoint_pattern': r'/api/.*',
                'method': '',
                'requests_per_minute': 100,
                'requests_per_hour': 1000,
                'requests_per_day': 10000,
            },
            {
                'name': 'Authentication',
                'endpoint_pattern': r'/api/auth/.*',
                'method': 'POST',
                'requests_per_minute': 10,
                'requests_per_hour': 50,
                'requests_per_day': 200,
            },
            {
                'name': 'Data Export',
                'endpoint_pattern': r'/api/database/.*/export/.*',
                'method': 'POST',
                'requests_per_minute': 2,
                'requests_per_hour': 10,
                'requests_per_day': 50,
            },
            {
                'name': 'GDPR Requests',
                'endpoint_pattern': r'/api/security/gdpr/.*',
                'method': 'POST',
                'requests_per_minute': 1,
                'requests_per_hour': 5,
                'requests_per_day': 10,
            },
        ]
        
        for rule_data in default_rules:
            rule, created = RateLimitRule.objects.get_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created rate limit rule: {rule.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Rate limit rule already exists: {rule.name}')
                )