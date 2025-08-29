"""
Handler for Zapier integration support.
"""
import json
import requests
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from celery import shared_task

from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.webhooks.handler import WebhookHandler
from .models import ZapierIntegration, ZapierExecution, MakeIntegration, MakeExecution


class ZapierIntegrationHandler:
    """Handler for Zapier integrations."""
    
    def create_integration(self, user, group, table, integration_type, **kwargs):
        """Create a new Zapier integration."""
        integration = ZapierIntegration.objects.create(
            group=group,
            table=table,
            integration_type=integration_type,
            created_by=user,
            **kwargs
        )
        
        return integration
    
    def get_trigger_data(self, integration, event_data):
        """Format data for Zapier trigger."""
        if integration.trigger_type == 'new_row':
            return self._format_row_data(integration.table, event_data.get('row'))
        elif integration.trigger_type == 'updated_row':
            return self._format_row_data(integration.table, event_data.get('row'))
        elif integration.trigger_type == 'deleted_row':
            return {
                'id': event_data.get('row_id'),
                'deleted_at': timezone.now().isoformat()
            }
        
        return event_data
    
    def execute_action(self, integration, input_data):
        """Execute a Zapier action."""
        execution = ZapierExecution.objects.create(
            integration=integration,
            input_data=input_data
        )
        
        try:
            start_time = timezone.now()
            
            if integration.action_type == 'create_row':
                result = self._create_row_action(integration, input_data)
            elif integration.action_type == 'update_row':
                result = self._update_row_action(integration, input_data)
            elif integration.action_type == 'delete_row':
                result = self._delete_row_action(integration, input_data)
            elif integration.action_type == 'find_row':
                result = self._find_row_action(integration, input_data)
            else:
                raise ValueError(f"Unknown action type: {integration.action_type}")
            
            end_time = timezone.now()
            execution_time = int((end_time - start_time).total_seconds() * 1000)
            
            execution.status = 'success'
            execution.output_data = result
            execution.execution_time_ms = execution_time
            execution.completed_at = end_time
            
            integration.successful_executions += 1
            
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            
            integration.failed_executions += 1
        
        finally:
            execution.save()
            integration.total_executions += 1
            integration.last_execution_at = timezone.now()
            integration.save()
        
        return execution
    
    def _format_row_data(self, table, row_data):
        """Format row data for Zapier consumption."""
        if not row_data:
            return {}
        
        formatted_data = {'id': row_data.get('id')}
        
        # Add field data with proper formatting
        for field in table.field_set.all():
            field_name = field.name
            field_value = row_data.get(f'field_{field.id}')
            
            # Format based on field type
            if field.type == 'date':
                if field_value:
                    formatted_data[field_name] = field_value.isoformat() if hasattr(field_value, 'isoformat') else field_value
            elif field.type == 'boolean':
                formatted_data[field_name] = bool(field_value)
            elif field.type == 'number':
                formatted_data[field_name] = float(field_value) if field_value is not None else None
            else:
                formatted_data[field_name] = field_value
        
        return formatted_data
    
    def _create_row_action(self, integration, input_data):
        """Execute create row action."""
        row_handler = RowHandler()
        
        # Convert Zapier field names back to Baserow format
        row_data = {}
        for field in integration.table.field_set.all():
            if field.name in input_data:
                row_data[f'field_{field.id}'] = input_data[field.name]
        
        row = row_handler.create_row_for_table(
            integration.created_by,
            integration.table,
            row_data
        )
        
        return self._format_row_data(integration.table, row_data)
    
    def _update_row_action(self, integration, input_data):
        """Execute update row action."""
        row_handler = RowHandler()
        row_id = input_data.get('id')
        
        if not row_id:
            raise ValueError("Row ID is required for update action")
        
        # Convert Zapier field names back to Baserow format
        row_data = {}
        for field in integration.table.field_set.all():
            if field.name in input_data:
                row_data[f'field_{field.id}'] = input_data[field.name]
        
        row = row_handler.update_row_by_id(
            integration.created_by,
            integration.table,
            row_id,
            row_data
        )
        
        return self._format_row_data(integration.table, row_data)
    
    def _delete_row_action(self, integration, input_data):
        """Execute delete row action."""
        row_handler = RowHandler()
        row_id = input_data.get('id')
        
        if not row_id:
            raise ValueError("Row ID is required for delete action")
        
        row_handler.delete_row_by_id(
            integration.created_by,
            integration.table,
            row_id
        )
        
        return {'id': row_id, 'deleted': True}
    
    def _find_row_action(self, integration, input_data):
        """Execute find row action."""
        table_model = integration.table.get_model()
        
        # Build search criteria
        search_criteria = {}
        for field in integration.table.field_set.all():
            if field.name in input_data:
                search_criteria[f'field_{field.id}'] = input_data[field.name]
        
        if not search_criteria:
            raise ValueError("At least one search criterion is required")
        
        try:
            row = table_model.objects.get(**search_criteria)
            row_data = {f'field_{field.id}': getattr(row, f'field_{field.id}') 
                       for field in integration.table.field_set.all()}
            row_data['id'] = row.id
            
            return self._format_row_data(integration.table, row_data)
        except table_model.DoesNotExist:
            return None


class MakeIntegrationHandler:
    """Handler for Make.com integrations."""
    
    def create_integration(self, user, group, table, module_type, **kwargs):
        """Create a new Make.com integration."""
        integration = MakeIntegration.objects.create(
            group=group,
            table=table,
            module_type=module_type,
            created_by=user,
            **kwargs
        )
        
        return integration
    
    def get_webhook_data(self, integration, event_data):
        """Format data for Make.com webhook."""
        # Similar to Zapier but with Make.com specific formatting
        return self._format_data_for_make(integration.table, event_data)
    
    def execute_module(self, integration, input_data):
        """Execute a Make.com module."""
        execution = MakeExecution.objects.create(
            integration=integration,
            input_data=input_data
        )
        
        try:
            start_time = timezone.now()
            
            if integration.module_type == 'action':
                result = self._execute_action_module(integration, input_data)
            elif integration.module_type == 'search':
                result = self._execute_search_module(integration, input_data)
            else:
                raise ValueError(f"Unknown module type: {integration.module_type}")
            
            end_time = timezone.now()
            execution_time = int((end_time - start_time).total_seconds() * 1000)
            
            execution.status = 'success'
            execution.output_data = result
            execution.execution_time_ms = execution_time
            execution.completed_at = end_time
            
            integration.successful_executions += 1
            
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            
            integration.failed_executions += 1
        
        finally:
            execution.save()
            integration.total_executions += 1
            integration.last_execution_at = timezone.now()
            integration.save()
        
        return execution
    
    def _format_data_for_make(self, table, event_data):
        """Format data for Make.com consumption."""
        # Similar to Zapier formatting but with Make.com conventions
        return self._format_row_data(table, event_data.get('row', {}))
    
    def _format_row_data(self, table, row_data):
        """Format row data for Make.com consumption."""
        if not row_data:
            return {}
        
        formatted_data = {'__id': row_data.get('id')}
        
        # Add field data with Make.com naming conventions
        for field in table.field_set.all():
            field_key = f"field_{field.id}"
            field_value = row_data.get(field_key)
            
            # Use field name as key for Make.com
            formatted_data[field.name] = field_value
        
        return formatted_data
    
    def _execute_action_module(self, integration, input_data):
        """Execute Make.com action module."""
        # Similar to Zapier actions but with Make.com specific handling
        action_type = integration.configuration.get('action_type', 'create_row')
        
        if action_type == 'create_row':
            return self._create_row_for_make(integration, input_data)
        elif action_type == 'update_row':
            return self._update_row_for_make(integration, input_data)
        elif action_type == 'delete_row':
            return self._delete_row_for_make(integration, input_data)
        
        raise ValueError(f"Unknown action type: {action_type}")
    
    def _execute_search_module(self, integration, input_data):
        """Execute Make.com search module."""
        table_model = integration.table.get_model()
        
        # Build search criteria from Make.com input
        search_criteria = {}
        for field in integration.table.field_set.all():
            if field.name in input_data:
                search_criteria[f'field_{field.id}'] = input_data[field.name]
        
        if not search_criteria:
            return []
        
        rows = table_model.objects.filter(**search_criteria)[:10]  # Limit results
        
        results = []
        for row in rows:
            row_data = {f'field_{field.id}': getattr(row, f'field_{field.id}') 
                       for field in integration.table.field_set.all()}
            row_data['id'] = row.id
            results.append(self._format_row_data(integration.table, row_data))
        
        return results
    
    def _create_row_for_make(self, integration, input_data):
        """Create row for Make.com action."""
        row_handler = RowHandler()
        
        # Convert Make.com field names to Baserow format
        row_data = {}
        for field in integration.table.field_set.all():
            if field.name in input_data:
                row_data[f'field_{field.id}'] = input_data[field.name]
        
        row = row_handler.create_row_for_table(
            integration.created_by,
            integration.table,
            row_data
        )
        
        return self._format_row_data(integration.table, row_data)
    
    def _update_row_for_make(self, integration, input_data):
        """Update row for Make.com action."""
        row_handler = RowHandler()
        row_id = input_data.get('__id') or input_data.get('id')
        
        if not row_id:
            raise ValueError("Row ID is required for update action")
        
        # Convert Make.com field names to Baserow format
        row_data = {}
        for field in integration.table.field_set.all():
            if field.name in input_data:
                row_data[f'field_{field.id}'] = input_data[field.name]
        
        row = row_handler.update_row_by_id(
            integration.created_by,
            integration.table,
            row_id,
            row_data
        )
        
        return self._format_row_data(integration.table, row_data)
    
    def _delete_row_for_make(self, integration, input_data):
        """Delete row for Make.com action."""
        row_handler = RowHandler()
        row_id = input_data.get('__id') or input_data.get('id')
        
        if not row_id:
            raise ValueError("Row ID is required for delete action")
        
        row_handler.delete_row_by_id(
            integration.created_by,
            integration.table,
            row_id
        )
        
        return {'__id': row_id, 'deleted': True}