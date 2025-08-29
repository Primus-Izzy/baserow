"""
Management command to initialize default action templates.
"""

from django.core.management.base import BaseCommand

from baserow.contrib.automation.nodes.action_template_handler import (
    ActionTemplateHandler
)


class Command(BaseCommand):
    help = 'Initialize default action templates for the automation system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing templates',
        )
    
    def handle(self, *args, **options):
        """Initialize action templates."""
        
        self.stdout.write('Initializing action templates...')
        
        try:
            handler = ActionTemplateHandler()
            
            if options['force']:
                # Delete existing system templates if force is specified
                from baserow.contrib.automation.nodes.enhanced_action_models import ActionTemplate
                deleted_count = ActionTemplate.objects.filter(is_system_template=True).delete()[0]
                self.stdout.write(f'Deleted {deleted_count} existing system templates')
            
            # Create system templates
            handler.create_system_templates()
            
            # Count created templates
            from baserow.contrib.automation.nodes.enhanced_action_models import ActionTemplate
            template_count = ActionTemplate.objects.filter(is_system_template=True).count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully initialized {template_count} action templates'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to initialize action templates: {e}')
            )
            raise