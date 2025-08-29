from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from typing import Dict, Any, Optional, List
import requests
import json
from urllib.parse import urlencode
from .models import (
    IntegrationProvider, 
    IntegrationConnection, 
    IntegrationSync, 
    IntegrationWebhook,
    IntegrationLog
)
from .exceptions import (
    IntegrationError,
    AuthenticationError,
    SyncError,
    ProviderNotFoundError
)


class IntegrationHandler:
    """Main handler for managing integrations"""
    
    def get_provider(self, provider_name: str) -> IntegrationProvider:
        """Get integration provider by name"""
        try:
            return IntegrationProvider.objects.get(name=provider_name, is_active=True)
        except IntegrationProvider.DoesNotExist:
            raise ProviderNotFoundError(f"Provider {provider_name} not found or inactive")
    
    def get_authorization_url(self, provider_name: str, user, workspace, state: str = None) -> str:
        """Generate OAuth authorization URL"""
        provider = self.get_provider(provider_name)
        
        redirect_uri = self._get_redirect_uri(provider_name)
        
        params = {
            'client_id': provider.client_id,
            'redirect_uri': redirect_uri,
            'scope': provider.scope,
            'response_type': 'code',
            'access_type': 'offline',  # For refresh tokens
            'prompt': 'consent',
        }
        
        if state:
            params['state'] = state
        
        return f"{provider.authorization_url}?{urlencode(params)}"
    
    def exchange_code_for_tokens(self, provider_name: str, code: str, user, workspace) -> IntegrationConnection:
        """Exchange authorization code for access tokens"""
        provider = self.get_provider(provider_name)
        
        data = {
            'client_id': provider.client_id,
            'client_secret': provider.decrypt_client_secret(),
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self._get_redirect_uri(provider_name),
        }
        
        try:
            response = requests.post(provider.token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            # Get user info from the provider
            user_info = self._get_user_info(provider, token_data['access_token'])
            
            # Create or update connection
            connection, created = IntegrationConnection.objects.update_or_create(
                user=user,
                workspace=workspace,
                provider=provider,
                defaults={
                    'access_token': connection.encrypt_token(token_data['access_token']) if hasattr(connection, 'encrypt_token') else token_data['access_token'],
                    'refresh_token': connection.encrypt_token(token_data.get('refresh_token', '')) if hasattr(connection, 'encrypt_token') else token_data.get('refresh_token', ''),
                    'token_expires_at': timezone.now() + timezone.timedelta(seconds=token_data.get('expires_in', 3600)),
                    'external_user_id': user_info.get('id', ''),
                    'external_user_email': user_info.get('email', ''),
                    'external_user_name': user_info.get('name', ''),
                    'status': 'active',
                    'error_message': '',
                }
            )
            
            self._log_integration_activity(connection, 'info', 'Connection established successfully')
            return connection
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Failed to exchange code for tokens: {str(e)}")
    
    def refresh_access_token(self, connection: IntegrationConnection) -> IntegrationConnection:
        """Refresh expired access token"""
        if not connection.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        provider = connection.provider
        
        data = {
            'client_id': provider.client_id,
            'client_secret': provider.decrypt_client_secret(),
            'refresh_token': connection.decrypt_access_token(),  # This should be decrypt_refresh_token
            'grant_type': 'refresh_token',
        }
        
        try:
            response = requests.post(provider.token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            connection.access_token = connection.encrypt_token(token_data['access_token'])
            if 'refresh_token' in token_data:
                connection.refresh_token = connection.encrypt_token(token_data['refresh_token'])
            connection.token_expires_at = timezone.now() + timezone.timedelta(seconds=token_data.get('expires_in', 3600))
            connection.status = 'active'
            connection.error_message = ''
            connection.save()
            
            self._log_integration_activity(connection, 'info', 'Access token refreshed successfully')
            return connection
            
        except requests.RequestException as e:
            connection.status = 'error'
            connection.error_message = f"Failed to refresh token: {str(e)}"
            connection.save()
            raise AuthenticationError(f"Failed to refresh access token: {str(e)}")
    
    def revoke_connection(self, connection: IntegrationConnection):
        """Revoke integration connection"""
        connection.status = 'revoked'
        connection.save()
        
        # Deactivate all syncs for this connection
        IntegrationSync.objects.filter(connection=connection).update(is_active=False)
        
        self._log_integration_activity(connection, 'info', 'Connection revoked')
    
    def create_sync(self, connection: IntegrationConnection, table, sync_config: Dict[str, Any]) -> IntegrationSync:
        """Create a new sync configuration"""
        sync = IntegrationSync.objects.create(
            connection=connection,
            table=table,
            sync_type=sync_config['sync_type'],
            sync_direction=sync_config.get('sync_direction', 'bidirectional'),
            external_resource_id=sync_config['external_resource_id'],
            field_mappings=sync_config.get('field_mappings', {}),
            sync_filters=sync_config.get('sync_filters', {}),
            auto_sync_enabled=sync_config.get('auto_sync_enabled', True),
            sync_interval_minutes=sync_config.get('sync_interval_minutes', 15),
        )
        
        self._log_integration_activity(connection, 'info', f'Sync created for {sync.sync_type}')
        return sync
    
    def _get_redirect_uri(self, provider_name: str) -> str:
        """Generate redirect URI for OAuth flow"""
        return f"{settings.PUBLIC_BACKEND_URL}/api/integrations/{provider_name}/callback/"
    
    def _get_user_info(self, provider: IntegrationProvider, access_token: str) -> Dict[str, Any]:
        """Get user information from the provider"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Provider-specific user info endpoints
        user_info_endpoints = {
            'google': 'https://www.googleapis.com/oauth2/v2/userinfo',
            'microsoft': 'https://graph.microsoft.com/v1.0/me',
            'slack': 'https://slack.com/api/users.identity',
            'dropbox': 'https://api.dropboxapi.com/2/users/get_current_account',
        }
        
        endpoint = user_info_endpoints.get(provider.provider_type)
        if not endpoint:
            return {}
        
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {}
    
    def _log_integration_activity(self, connection: IntegrationConnection, level: str, message: str, details: Dict[str, Any] = None):
        """Log integration activity"""
        IntegrationLog.objects.create(
            connection=connection,
            level=level,
            message=message,
            details=details or {}
        )


class GoogleIntegrationHandler:
    """Handler for Google services (Drive, Calendar, Gmail)"""
    
    def __init__(self, connection: IntegrationConnection):
        self.connection = connection
        self.base_url = "https://www.googleapis.com"
    
    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.connection.decrypt_access_token()}',
            'Content-Type': 'application/json'
        }
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """List user's Google Calendars"""
        url = f"{self.base_url}/calendar/v3/users/me/calendarList"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json().get('items', [])
    
    def create_calendar_event(self, calendar_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create event in Google Calendar"""
        url = f"{self.base_url}/calendar/v3/calendars/{calendar_id}/events"
        response = requests.post(url, headers=self.get_headers(), json=event_data)
        response.raise_for_status()
        return response.json()
    
    def list_drive_files(self, folder_id: str = None) -> List[Dict[str, Any]]:
        """List files in Google Drive"""
        url = f"{self.base_url}/drive/v3/files"
        params = {'pageSize': 100}
        if folder_id:
            params['q'] = f"'{folder_id}' in parents"
        
        response = requests.get(url, headers=self.get_headers(), params=params)
        response.raise_for_status()
        return response.json().get('files', [])
    
    def upload_file_to_drive(self, file_data: bytes, filename: str, folder_id: str = None) -> Dict[str, Any]:
        """Upload file to Google Drive"""
        metadata = {'name': filename}
        if folder_id:
            metadata['parents'] = [folder_id]
        
        files = {
            'data': ('metadata', json.dumps(metadata), 'application/json; charset=UTF-8'),
            'file': (filename, file_data)
        }
        
        url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        headers = {'Authorization': f'Bearer {self.connection.decrypt_access_token()}'}
        
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return response.json()


class MicrosoftIntegrationHandler:
    """Handler for Microsoft services (OneDrive, Outlook, Teams)"""
    
    def __init__(self, connection: IntegrationConnection):
        self.connection = connection
        self.base_url = "https://graph.microsoft.com/v1.0"
    
    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.connection.decrypt_access_token()}',
            'Content-Type': 'application/json'
        }
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """List user's Outlook calendars"""
        url = f"{self.base_url}/me/calendars"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json().get('value', [])
    
    def create_calendar_event(self, calendar_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create event in Outlook calendar"""
        url = f"{self.base_url}/me/calendars/{calendar_id}/events"
        response = requests.post(url, headers=self.get_headers(), json=event_data)
        response.raise_for_status()
        return response.json()
    
    def list_onedrive_files(self, folder_id: str = None) -> List[Dict[str, Any]]:
        """List files in OneDrive"""
        if folder_id:
            url = f"{self.base_url}/me/drive/items/{folder_id}/children"
        else:
            url = f"{self.base_url}/me/drive/root/children"
        
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json().get('value', [])
    
    def upload_file_to_onedrive(self, file_data: bytes, filename: str, folder_id: str = None) -> Dict[str, Any]:
        """Upload file to OneDrive"""
        if folder_id:
            url = f"{self.base_url}/me/drive/items/{folder_id}:/{filename}:/content"
        else:
            url = f"{self.base_url}/me/drive/root:/{filename}:/content"
        
        headers = {
            'Authorization': f'Bearer {self.connection.decrypt_access_token()}',
            'Content-Type': 'application/octet-stream'
        }
        
        response = requests.put(url, headers=headers, data=file_data)
        response.raise_for_status()
        return response.json()
    
    def list_teams(self) -> List[Dict[str, Any]]:
        """List user's Microsoft Teams"""
        url = f"{self.base_url}/me/joinedTeams"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json().get('value', [])
    
    def list_team_channels(self, team_id: str) -> List[Dict[str, Any]]:
        """List channels in a Microsoft Team"""
        url = f"{self.base_url}/teams/{team_id}/channels"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json().get('value', [])
    
    def send_teams_message(self, team_id: str, channel_id: str, message: str) -> Dict[str, Any]:
        """Send message to Microsoft Teams channel"""
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages"
        
        message_data = {
            'body': {
                'content': message,
                'contentType': 'text'
            }
        }
        
        response = requests.post(url, headers=self.get_headers(), json=message_data)
        response.raise_for_status()
        return response.json()
    
    def create_teams_meeting(self, subject: str, start_time: str, end_time: str, attendees: List[str] = None) -> Dict[str, Any]:
        """Create a Microsoft Teams meeting"""
        url = f"{self.base_url}/me/onlineMeetings"
        
        meeting_data = {
            'subject': subject,
            'startDateTime': start_time,
            'endDateTime': end_time,
        }
        
        if attendees:
            meeting_data['participants'] = {
                'attendees': [{'identity': {'user': {'id': attendee}}} for attendee in attendees]
            }
        
        response = requests.post(url, headers=self.get_headers(), json=meeting_data)
        response.raise_for_status()
        return response.json()


class SlackIntegrationHandler:
    """Handler for Slack integration"""
    
    def __init__(self, connection: IntegrationConnection):
        self.connection = connection
        self.base_url = "https://slack.com/api"
    
    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.connection.decrypt_access_token()}',
            'Content-Type': 'application/json'
        }
    
    def send_message(self, channel: str, text: str, attachments: List[Dict] = None) -> Dict[str, Any]:
        """Send message to Slack channel"""
        url = f"{self.base_url}/chat.postMessage"
        data = {
            'channel': channel,
            'text': text
        }
        if attachments:
            data['attachments'] = attachments
        
        response = requests.post(url, headers=self.get_headers(), json=data)
        response.raise_for_status()
        return response.json()
    
    def list_channels(self) -> List[Dict[str, Any]]:
        """List Slack channels"""
        url = f"{self.base_url}/conversations.list"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json().get('channels', [])


class DropboxIntegrationHandler:
    """Handler for Dropbox integration"""
    
    def __init__(self, connection: IntegrationConnection):
        self.connection = connection
        self.base_url = "https://api.dropboxapi.com/2"
    
    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.connection.decrypt_access_token()}',
            'Content-Type': 'application/json'
        }
    
    def list_files(self, folder_path: str = "") -> List[Dict[str, Any]]:
        """List files in Dropbox folder"""
        url = f"{self.base_url}/files/list_folder"
        data = {'path': folder_path}
        
        response = requests.post(url, headers=self.get_headers(), json=data)
        response.raise_for_status()
        return response.json().get('entries', [])
    
    def upload_file(self, file_data: bytes, file_path: str) -> Dict[str, Any]:
        """Upload file to Dropbox"""
        url = "https://content.dropboxapi.com/2/files/upload"
        headers = {
            'Authorization': f'Bearer {self.connection.decrypt_access_token()}',
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': json.dumps({'path': file_path, 'mode': 'add'})
        }
        
        response = requests.post(url, headers=headers, data=file_data)
        response.raise_for_status()
        return response.json()
    
    def create_shared_link(self, file_path: str) -> Dict[str, Any]:
        """Create a shared link for a Dropbox file"""
        url = f"{self.base_url}/sharing/create_shared_link_with_settings"
        data = {
            'path': file_path,
            'settings': {
                'requested_visibility': 'public',
                'audience': 'public',
                'access': 'viewer'
            }
        }
        
        response = requests.post(url, headers=self.get_headers(), json=data)
        response.raise_for_status()
        return response.json()


class EmailIntegrationHandler:
    """Handler for email service integration"""
    
    def __init__(self, connection: IntegrationConnection):
        self.connection = connection
        self.smtp_settings = self._get_smtp_settings()
    
    def _get_smtp_settings(self) -> Dict[str, Any]:
        """Get SMTP settings based on provider"""
        provider_settings = {
            'gmail': {
                'host': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True
            },
            'outlook': {
                'host': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True
            },
            'yahoo': {
                'host': 'smtp.mail.yahoo.com',
                'port': 587,
                'use_tls': True
            }
        }
        
        provider_type = self.connection.provider.provider_type
        return provider_settings.get(provider_type, {})
    
    def send_email(self, to_emails: List[str], subject: str, body: str, html_body: str = None, attachments: List[Dict] = None) -> bool:
        """Send email using SMTP"""
        from django.core.mail import EmailMultiAlternatives
        from django.core.mail.backends.smtp import EmailBackend
        from django.conf import settings
        import tempfile
        import base64
        
        try:
            # Create custom SMTP backend with connection credentials
            backend = EmailBackend(
                host=self.smtp_settings.get('host'),
                port=self.smtp_settings.get('port'),
                username=self.connection.external_user_email,
                password=self.connection.decrypt_access_token(),  # For app passwords
                use_tls=self.smtp_settings.get('use_tls', True),
                fail_silently=False
            )
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=self.connection.external_user_email,
                to=to_emails,
                connection=backend
            )
            
            # Add HTML alternative if provided
            if html_body:
                email.attach_alternative(html_body, "text/html")
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    if 'content' in attachment and 'filename' in attachment:
                        # Decode base64 content if needed
                        content = attachment['content']
                        if isinstance(content, str):
                            content = base64.b64decode(content)
                        
                        email.attach(
                            attachment['filename'],
                            content,
                            attachment.get('content_type', 'application/octet-stream')
                        )
            
            # Send email
            email.send()
            return True
            
        except Exception as e:
            self._log_error(f"Failed to send email: {str(e)}")
            return False
    
    def validate_connection(self) -> bool:
        """Validate email connection"""
        try:
            from django.core.mail.backends.smtp import EmailBackend
            
            backend = EmailBackend(
                host=self.smtp_settings.get('host'),
                port=self.smtp_settings.get('port'),
                username=self.connection.external_user_email,
                password=self.connection.decrypt_access_token(),
                use_tls=self.smtp_settings.get('use_tls', True),
                fail_silently=False
            )
            
            # Test connection
            backend.open()
            backend.close()
            return True
            
        except Exception as e:
            self._log_error(f"Email connection validation failed: {str(e)}")
            return False
    
    def _log_error(self, message: str):
        """Log error message"""
        from .models import IntegrationLog
        IntegrationLog.objects.create(
            connection=self.connection,
            level='error',
            message=message
        )