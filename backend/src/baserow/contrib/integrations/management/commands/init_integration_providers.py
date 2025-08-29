from django.core.management.base import BaseCommand
from baserow.contrib.integrations.models import IntegrationProvider


class Command(BaseCommand):
    help = 'Initialize default integration providers'

    def handle(self, *args, **options):
        providers = [
            {
                'name': 'google',
                'provider_type': 'google',
                'display_name': 'Google',
                'description': 'Connect to Google Drive, Calendar, and Gmail',
                'authorization_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'scope': 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/gmail.send',
                'api_base_url': 'https://www.googleapis.com',
            },
            {
                'name': 'microsoft',
                'provider_type': 'microsoft',
                'display_name': 'Microsoft',
                'description': 'Connect to OneDrive, Outlook, and Teams',
                'authorization_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
                'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                'scope': 'https://graph.microsoft.com/Files.ReadWrite https://graph.microsoft.com/Calendars.ReadWrite https://graph.microsoft.com/Mail.Send',
                'api_base_url': 'https://graph.microsoft.com/v1.0',
            },
            {
                'name': 'slack',
                'provider_type': 'slack',
                'display_name': 'Slack',
                'description': 'Send notifications and messages to Slack',
                'authorization_url': 'https://slack.com/oauth/v2/authorize',
                'token_url': 'https://slack.com/api/oauth.v2.access',
                'scope': 'chat:write channels:read groups:read',
                'api_base_url': 'https://slack.com/api',
            },
            {
                'name': 'dropbox',
                'provider_type': 'dropbox',
                'display_name': 'Dropbox',
                'description': 'Connect to Dropbox for file storage',
                'authorization_url': 'https://www.dropbox.com/oauth2/authorize',
                'token_url': 'https://api.dropboxapi.com/oauth2/token',
                'scope': 'files.content.write files.content.read',
                'api_base_url': 'https://api.dropboxapi.com/2',
            },
            {
                'name': 'email',
                'provider_type': 'email',
                'display_name': 'Email Services',
                'description': 'Send emails through Gmail, Outlook, or other SMTP providers',
                'authorization_url': '',  # Email uses app passwords, not OAuth
                'token_url': '',
                'scope': '',
                'api_base_url': '',
            },
        ]

        for provider_data in providers:
            provider, created = IntegrationProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults=provider_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created provider: {provider.display_name}')
                )
            else:
                self.stdout.write(f'Provider already exists: {provider.display_name}')

        self.stdout.write(self.style.SUCCESS('Integration providers initialized'))