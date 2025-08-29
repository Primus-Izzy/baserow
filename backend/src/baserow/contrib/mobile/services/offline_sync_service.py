"""
Offline synchronization service
"""

import logging
from typing import Dict, Any
from django.db import transaction
from django.utils import timezone

from ..models import OfflineOperation
from baserow.contrib.database.models import Table, Row
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.views.handler import ViewHandler

logger = logging.getLogger(__name__)


class OfflineSyncService:
    """Service for synchronizing offline operations"""
    
    def __init__(self):
        self.row_handler = RowHandler()
        self.field_handler = FieldHandler()
        self.view_handler = ViewHandler()
    
    def sync_operation(self, operation: OfflineOperation) -> bool:
        """
        Sync a single offline operation
        
        Args:
            operation: OfflineOperation instance to sync
            
        Returns:
            bool: True if synced successfully, False otherwise
        """
        try:
            with transaction.atomic():
                success = self._execute_operation(operation)
                
                if success:
                    operation.mark_synced()
                    logger.info(f"Successfully synced operation {operation.id}")
                    return True
                else:
                    operation.mark_failed("Operation execution failed")
                    return False
                    
        except Exception as e:
            error_message = str(e)
            logger.error(f"Failed to sync operation {operation.id}: {error_message}")
            operation.mark_failed(error_message)
            return False
    
    def _execute_operation(self, operation: OfflineOperation) -> bool:
        """Execute the specific operation based on its type"""
        operation_type = operation.operation_type
        data = operation.data
        
        try:
            if operation_type == 'create_row':
                return self._sync_create_row(operation, data)
            elif operation_type == 'update_row':
                return self._sync_update_row(operation, data)
            elif operation_type == 'delete_row':
                return self._sync_delete_row(operation, data)
            elif operation_type == 'update_field':
                return self._sync_update_field(operation, data)
            elif operation_type == 'create_view':
                return self._sync_create_view(operation, data)
            elif operation_type == 'update_view':
                return self._sync_update_view(operation, data)
            else:
                logger.error(f"Unknown operation type: {operation_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing {operation_type}: {e}")
            return False
    
    def _sync_create_row(self, operation: OfflineOperation, data: Dict[str, Any]) -> bool:
        """Sync row creation"""
        try:
            table = Table.objects.get(id=operation.table_id)
            
            # Create the row
            row = self.row_handler.create_row_for_table(
                user=operation.user,
                table=table,
                values=data.get('values', {}),
                before_id=data.get('before_id')
            )
            
            # Update operation with the created row ID
            operation.row_id = row.id
            operation.save()
            
            return True
            
        except Table.DoesNotExist:
            logger.error(f"Table {operation.table_id} not found for create_row operation")
            return False
        except Exception as e:
            logger.error(f"Failed to create row: {e}")
            return False
    
    def _sync_update_row(self, operation: OfflineOperation, data: Dict[str, Any]) -> bool:
        """Sync row update"""
        try:
            table = Table.objects.get(id=operation.table_id)
            
            # Get the row
            row = self.row_handler.get_row_for_table(
                user=operation.user,
                table=table,
                row_id=operation.row_id
            )
            
            # Update the row
            self.row_handler.update_row_for_table(
                user=operation.user,
                table=table,
                row_id=operation.row_id,
                values=data.get('values', {})
            )
            
            return True
            
        except (Table.DoesNotExist, Row.DoesNotExist):
            logger.error(f"Table {operation.table_id} or row {operation.row_id} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to update row: {e}")
            return False
    
    def _sync_delete_row(self, operation: OfflineOperation, data: Dict[str, Any]) -> bool:
        """Sync row deletion"""
        try:
            table = Table.objects.get(id=operation.table_id)
            
            # Delete the row
            self.row_handler.delete_row_for_table(
                user=operation.user,
                table=table,
                row_id=operation.row_id
            )
            
            return True
            
        except (Table.DoesNotExist, Row.DoesNotExist):
            # Row might already be deleted, consider this a success
            logger.warning(f"Table {operation.table_id} or row {operation.row_id} not found for deletion")
            return True
        except Exception as e:
            logger.error(f"Failed to delete row: {e}")
            return False
    
    def _sync_update_field(self, operation: OfflineOperation, data: Dict[str, Any]) -> bool:
        """Sync field update"""
        try:
            field_id = data.get('field_id')
            field_data = data.get('field_data', {})
            
            # Get the field
            field = self.field_handler.get_field(field_id)
            
            # Update the field
            self.field_handler.update_field(
                user=operation.user,
                field=field,
                **field_data
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update field: {e}")
            return False
    
    def _sync_create_view(self, operation: OfflineOperation, data: Dict[str, Any]) -> bool:
        """Sync view creation"""
        try:
            table = Table.objects.get(id=operation.table_id)
            view_type = data.get('view_type', 'grid')
            view_data = data.get('view_data', {})
            
            # Create the view
            view = self.view_handler.create_view(
                user=operation.user,
                table=table,
                type_name=view_type,
                **view_data
            )
            
            # Store the created view ID in the operation data
            operation.data['view_id'] = view.id
            operation.save()
            
            return True
            
        except Table.DoesNotExist:
            logger.error(f"Table {operation.table_id} not found for create_view operation")
            return False
        except Exception as e:
            logger.error(f"Failed to create view: {e}")
            return False
    
    def _sync_update_view(self, operation: OfflineOperation, data: Dict[str, Any]) -> bool:
        """Sync view update"""
        try:
            view_id = data.get('view_id')
            view_data = data.get('view_data', {})
            
            # Get the view
            view = self.view_handler.get_view(view_id)
            
            # Update the view
            self.view_handler.update_view(
                user=operation.user,
                view=view,
                **view_data
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update view: {e}")
            return False
    
    def sync_user_operations(self, user, limit: int = 100) -> Dict[str, int]:
        """
        Sync all pending operations for a user
        
        Args:
            user: User instance
            limit: Maximum number of operations to sync
            
        Returns:
            Dict with sync statistics
        """
        pending_operations = OfflineOperation.objects.filter(
            user=user,
            status='pending'
        ).order_by('created_at')[:limit]
        
        stats = {
            'total': pending_operations.count(),
            'synced': 0,
            'failed': 0
        }
        
        for operation in pending_operations:
            if self.sync_operation(operation):
                stats['synced'] += 1
            else:
                stats['failed'] += 1
        
        logger.info(f"Sync completed for user {user.id}: {stats}")
        return stats
    
    def queue_operation(
        self,
        user,
        operation_type: str,
        table_id: int = None,
        row_id: int = None,
        data: Dict[str, Any] = None
    ) -> OfflineOperation:
        """
        Queue an operation for later sync
        
        Args:
            user: User performing the operation
            operation_type: Type of operation
            table_id: Table ID (if applicable)
            row_id: Row ID (if applicable)
            data: Operation data
            
        Returns:
            OfflineOperation instance
        """
        operation = OfflineOperation.objects.create(
            user=user,
            operation_type=operation_type,
            table_id=table_id,
            row_id=row_id,
            data=data or {}
        )
        
        logger.info(f"Queued {operation_type} operation {operation.id} for user {user.id}")
        return operation
    
    def get_sync_status(self, user) -> Dict[str, Any]:
        """Get sync status for a user"""
        pending_count = OfflineOperation.objects.filter(
            user=user,
            status='pending'
        ).count()
        
        last_sync = OfflineOperation.objects.filter(
            user=user,
            status='synced'
        ).order_by('-synced_at').first()
        
        failed_count = OfflineOperation.objects.filter(
            user=user,
            status='failed'
        ).count()
        
        return {
            'pending_operations': pending_count,
            'failed_operations': failed_count,
            'last_sync_time': last_sync.synced_at if last_sync else None,
            'total_operations': OfflineOperation.objects.filter(user=user).count()
        }
    
    def cleanup_old_operations(self, days_old: int = 30) -> int:
        """Clean up old synced operations"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
        
        deleted_count = OfflineOperation.objects.filter(
            status='synced',
            synced_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old synced operations")
        return deleted_count
    
    def retry_failed_operations(self, user, max_retries: int = 3) -> Dict[str, int]:
        """Retry failed operations that haven't exceeded max retries"""
        failed_operations = OfflineOperation.objects.filter(
            user=user,
            status='failed',
            retry_count__lt=max_retries
        ).order_by('created_at')
        
        stats = {
            'total': failed_operations.count(),
            'synced': 0,
            'failed': 0
        }
        
        for operation in failed_operations:
            # Reset status to pending for retry
            operation.status = 'pending'
            operation.error_message = ''
            operation.save()
            
            if self.sync_operation(operation):
                stats['synced'] += 1
            else:
                stats['failed'] += 1
        
        logger.info(f"Retry completed for user {user.id}: {stats}")
        return stats