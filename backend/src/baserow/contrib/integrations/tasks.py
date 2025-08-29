from celery import shared_task
from django.utils import timezone
from typing import Dict, Any
import logging
from .models import IntegrationSync, IntegrationConnection
from .handler import (
    GoogleIntegrationHandler,
    MicrosoftIntegrationHandler,
    SlackIntegrationHandler,
    DropboxIntegrationHandler
)
from .exceptions import SyncError, AuthenticationError

logger = logging.getLogger(__name__)


@shared_task
def run_integration_sync(sync_id: str):
    """Run integration sync for a specific sync configuration"""
    try:
        sync = IntegrationSync.objects.get(id=sync_id, is_active=True)
        connection = sync.connection
        
        if connection.status != 'active':
            logger.warning(f"Skipping sync {sync_id} - connection not active")
            return
        
        # Update sync status
        sync.last_sync_status = 'running'
        sync.save()
        
        # Get appropriate handler based on provider
        handler = _get_integration_handler(connection)
        
        # Perform sync based on sync type
        if sync.sync_type == 'calendar':
            _sync_calendar_data(sync, handler)
        elif sync.sync_type == 'file_storage':
            _sync_file_storage(sync, handler)
        elif sync.sync_type == 'notifications':
            _sync_notifications(sync, handler)
        
        # Update sync status
        sync.last_sync_at = timezone.now()
        sync.last_sync_status = 'success'
        sync.sync_error_message = ''
        sync.save()
        
        logger.info(f"Sync {sync_id} completed successfully")
        
    except IntegrationSync.DoesNotExist:
        logger.error(f"Sync {sync_id} not found")
    except Exception as e:
        logger.error(f"Sync {sync_id} failed: {str(e)}")
        try:
            sync = IntegrationSync.objects.get(id=sync_id)
            sync.last_sync_status = 'error'
            sync.sync_error_message = str(e)
            sync.save()
        except IntegrationSync.DoesNotExist:
            pass


@shared_task
def run_scheduled_syncs():
    """Run all scheduled syncs that are due"""
    now = timezone.now()
    
    # Find syncs that are due for execution
    due_syncs = IntegrationSync.objects.filter(
        is_active=True,
        auto_sync_enabled=True,
        connection__status='active'
    ).exclude(last_sync_status='running')
    
    for sync in due_syncs:
        # Check if sync is due based on interval
        if sync.last_sync_at:
            next_sync_time = sync.last_sync_at + timezone.timedelta(minutes=sync.sync_interval_minutes)
            if now < next_sync_time:
                continue
        
        # Trigger sync
        run_integration_sync.delay(str(sync.id))


@shared_task
def refresh_expired_tokens():
    """Refresh expired access tokens"""
    from .handler import IntegrationHandler
    
    now = timezone.now()
    expired_connections = IntegrationConnection.objects.filter(
        status='active',
        token_expires_at__lt=now
    )
    
    handler = IntegrationHandler()
    
    for connection in expired_connections:
        try:
            handler.refresh_access_token(connection)
            logger.info(f"Refreshed token for connection {connection.id}")
        except AuthenticationError as e:
            logger.error(f"Failed to refresh token for connection {connection.id}: {str(e)}")


def _get_integration_handler(connection: IntegrationConnection):
    """Get appropriate integration handler based on provider type"""
    provider_type = connection.provider.provider_type
    
    if provider_type == 'google':
        return GoogleIntegrationHandler(connection)
    elif provider_type == 'microsoft':
        return MicrosoftIntegrationHandler(connection)
    elif provider_type == 'slack':
        return SlackIntegrationHandler(connection)
    elif provider_type == 'dropbox':
        return DropboxIntegrationHandler(connection)
    else:
        raise SyncError(f"Unsupported provider type: {provider_type}")


def _sync_calendar_data(sync: IntegrationSync, handler):
    """Sync calendar data between Baserow and external calendar"""
    from baserow.contrib.database.rows.handler import RowHandler
    from baserow.contrib.database.fields.handler import FieldHandler
    
    table = sync.table
    field_mappings = sync.field_mappings
    
    try:
        if sync.sync_direction in ['bidirectional', 'import_only']:
            # Import events from external calendar
            if hasattr(handler, 'list_calendar_events'):
                external_events = handler.list_calendar_events(sync.external_resource_id)
                
                row_handler = RowHandler()
                
                for event in external_events:
                    # Map external event data to Baserow fields
                    row_data = {}
                    for baserow_field, external_field in field_mappings.items():
                        if external_field in event:
                            row_data[baserow_field] = event[external_field]
                    
                    # Create or update row in Baserow
                    if row_data:
                        row_handler.create_row_for_table(
                            user=sync.connection.user,
                            table=table,
                            values=row_data
                        )
        
        if sync.sync_direction in ['bidirectional', 'export_only']:
            # Export Baserow rows to external calendar
            from baserow.contrib.database.rows.models import Row
            
            # Get rows from Baserow table
            rows = table.get_model().objects.all()
            
            for row in rows:
                # Map Baserow row data to external event format
                event_data = {}
                for baserow_field, external_field in field_mappings.items():
                    field_value = getattr(row, f'field_{baserow_field}', None)
                    if field_value is not None:
                        event_data[external_field] = str(field_value)
                
                # Create event in external calendar
                if event_data and hasattr(handler, 'create_calendar_event'):
                    handler.create_calendar_event(sync.external_resource_id, event_data)
                    
    except Exception as e:
        logger.error(f"Calendar sync failed for sync {sync.id}: {str(e)}")
        raise SyncError(f"Calendar sync failed: {str(e)}")


def _sync_file_storage(sync: IntegrationSync, handler):
    """Sync file storage data"""
    from baserow.contrib.database.fields.models import FileField
    from baserow.core.user_files.handler import UserFileHandler
    
    table = sync.table
    
    try:
        if sync.sync_direction in ['bidirectional', 'import_only']:
            # Import files from external storage
            if hasattr(handler, 'list_files'):
                external_files = handler.list_files(sync.external_resource_id)
                
                # Find file fields in the table
                file_fields = table.field_set.filter(content_type__model='filefield')
                
                for file_field in file_fields:
                    for external_file in external_files:
                        # Download and import file logic would go here
                        pass
        
        if sync.sync_direction in ['bidirectional', 'export_only']:
            # Export files from Baserow to external storage
            file_fields = table.field_set.filter(content_type__model='filefield')
            
            for file_field in file_fields:
                # Get all file values for this field
                rows = table.get_model().objects.all()
                
                for row in rows:
                    file_value = getattr(row, f'field_{file_field.id}', None)
                    if file_value:
                        # Upload file to external storage
                        if hasattr(handler, 'upload_file'):
                            # File upload logic would go here
                            pass
                            
    except Exception as e:
        logger.error(f"File storage sync failed for sync {sync.id}: {str(e)}")
        raise SyncError(f"File storage sync failed: {str(e)}")


def _sync_notifications(sync: IntegrationSync, handler):
    """Sync notification data"""
    from baserow.contrib.database.notifications.handler import notification_handler
    
    table = sync.table
    field_mappings = sync.field_mappings
    
    try:
        if sync.sync_direction in ['bidirectional', 'export_only']:
            # Send notifications based on Baserow data changes
            
            # Get recent rows or changes (this would need to be tracked)
            rows = table.get_model().objects.all()[:10]  # Limit for demo
            
            for row in rows:
                # Build notification message from row data
                message_parts = []
                for baserow_field, external_field in field_mappings.items():
                    field_value = getattr(row, f'field_{baserow_field}', None)
                    if field_value:
                        message_parts.append(f"{external_field}: {field_value}")
                
                message = f"Baserow Update: {', '.join(message_parts)}"
                
                # Send notification via appropriate handler
                if hasattr(handler, 'send_message'):
                    handler.send_message(sync.external_resource_id, message)
                elif hasattr(handler, 'send_teams_message'):
                    # For Teams, we need team_id and channel_id
                    # This would need to be stored in sync configuration
                    pass
                    
    except Exception as e:
        logger.error(f"Notification sync failed for sync {sync.id}: {str(e)}")
        raise SyncError(f"Notification sync failed: {str(e)}")


@shared_task
def cleanup_integration_logs():
    """Clean up old integration logs"""
    from .models import IntegrationLog
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = IntegrationLog.objects.filter(
        created_at__lt=cutoff_date
    ).delete()
    
    logger.info(f"Cleaned up {deleted_count} old integration logs")


@shared_task
def test_integration_connections():
    """Test all active integration connections"""
    from .handler import IntegrationHandler
    
    active_connections = IntegrationConnection.objects.filter(status='active')
    handler = IntegrationHandler()
    
    for connection in active_connections:
        try:
            # Test connection by making a simple API call
            integration_handler = _get_integration_handler(connection)
            
            # Provider-specific health checks
            if connection.provider.provider_type == 'google':
                integration_handler.list_calendars()
            elif connection.provider.provider_type == 'microsoft':
                integration_handler.list_calendars()
            elif connection.provider.provider_type == 'slack':
                integration_handler.list_channels()
            elif connection.provider.provider_type == 'dropbox':
                integration_handler.list_files()
            
            # Connection is healthy
            if connection.status != 'active':
                connection.status = 'active'
                connection.error_message = ''
                connection.save()
                
        except AuthenticationError:
            # Try to refresh token
            try:
                handler.refresh_access_token(connection)
            except AuthenticationError:
                connection.status = 'expired'
                connection.save()
        except Exception as e:
            connection.status = 'error'
            connection.error_message = str(e)
            connection.save()
            logger.error(f"Connection {connection.id} health check failed: {str(e)}")