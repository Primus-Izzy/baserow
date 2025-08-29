"""
Management command to initialize default trigger templates.

This command creates the default trigger templates that should be available
in all Baserow installations.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from baserow.contrib.automation.nodes.enhanced_trigger_models import TriggerTemplate
from baserow.contrib.automation.nodes.trigger_template_handler import get_default_templates


class Command(BaseCommand):
    help = 'Initialize default trigger templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing templates',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write('Initializing default trigger templates...')
        
        default_templates = get_default_templates()
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for template_data in default_templates:
                template_name = template_data['name']
                
                if force:
                    # Delete existing template if force is enabled
                    TriggerTemplate.objects.filter(name=template_name).delete()
                
                # Check if template already exists
                existing_template = TriggerTemplate.objects.filter(name=template_name).first()
                
                if existing_template:
                    if not force:
                        self.stdout.write(
                            self.style.WARNING(f'Template "{template_name}" already exists, skipping...')
                        )
                        continue
                
                # Create or update the template
                template, created = TriggerTemplate.objects.update_or_create(
                    name=template_name,
                    defaults=template_data
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created template: "{template_name}"')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated template: "{template_name}"')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized {created_count} new templates '
                f'and updated {updated_count} existing templates.'
            )
        )
        
        # Display summary of available templates
        total_templates = TriggerTemplate.objects.filter(is_active=True).count()
        self.stdout.write(f'Total active templates: {total_templates}')
        
        # Display templates by category
        categories = TriggerTemplate.objects.values_list('category', flat=True).distinct()
        for category in categories:
            count = TriggerTemplate.objects.filter(category=category, is_active=True).count()
            self.stdout.write(f'  {category}: {count} templates')