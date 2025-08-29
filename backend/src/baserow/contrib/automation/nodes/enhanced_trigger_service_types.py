"""
Enhanced trigger service types for the automation system.

This module contains service types for date-based triggers, linked record change triggers,
external webhook triggers, and conditional trigger evaluation.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable

from django.db.models import QuerySet
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import transaction

from baserow.core.services.registries import ServiceType
from baserow.core.services.types import DispatchResult
from baserow.core.services.registries import TriggerServiceTypeMixin
from baserow.contrib.database.fields.models import Field, LinkRowField, DateField
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.automation.nodes.enhanced_trigger_models import (
    DateBasedTriggerNode,
    LinkedRecordChangeTriggerNode,
    WebhookTriggerNode,
    ConditionalTriggerNode,
)

logger = logging.getLogger(__name__)


class DateBasedTriggerServiceType(TriggerServiceTypeMixin, ServiceType):
    """
    Service type for date-based triggers.
    Handles scheduled triggers, date reached triggers, and recurring patterns.
    """
    
    type = "date_based_trigger"
    model_class = DateBasedTriggerNode
    returns_list = True
    
    def __init__(self):
        self.scheduled_checks = {}
        self.on_event = None
    
    def start_listening(self, on_event: Callable):
        """Start listening for date-based trigger events."""
        self.on_event = on_event
        # Schedule periodic checks for date-based triggers
        self._schedule_periodic_checks()
    
    def stop_listening(self):
        """Stop listening for date-based trigger events."""
        self.on_event = None
        # Cancel scheduled checks
        self._cancel_periodic_checks()
    
    def _schedule_periodic_checks(self):
        """Schedule periodic checks for date-based triggers."""
        from celery import current_app
        
        # Schedule a task to check date-based triggers every hour
        current_app.send_task(
            'baserow.contrib.automation.tasks.check_date_based_triggers',
            countdown=3600,  # Check every hour
        )
    
    def _cancel_periodic_checks(self):
        """Cancel scheduled periodic checks."""
        # Implementation would cancel scheduled Celery tasks
        pass
    
    def check_date_triggers(self):
        """Check all date-based triggers and fire those that match conditions."""
        if not self.on_event:
            return
        
        now = timezone.now()
        
        # Get all active date-based trigger nodes
        trigger_nodes = self.model_class.objects.filter(
            workflow__published=True,
            workflow__paused=False
        ).select_related('date_field', 'workflow')
        
        for trigger_node in trigger_nodes:
            try:
                if self._should_trigger(trigger_node, now):
                    # Get rows that match the trigger condition
                    matching_rows = self._get_matching_rows(trigger_node, now)
                    
                    if matching_rows:
                        # Fire the trigger with matching rows
                        self.on_event(
                            self.model_class.objects.filter(id=trigger_node.id),
                            matching_rows,
                            user=None  # System-triggered
                        )
            except Exception as e:
                logger.error(f"Error checking date trigger {trigger_node.id}: {e}")
    
    def _should_trigger(self, trigger_node: DateBasedTriggerNode, now: datetime) -> bool:
        """Check if a date trigger should fire based on its conditions."""
        condition_type = trigger_node.condition_type
        
        if condition_type == 'recurring':
            return self._check_recurring_condition(trigger_node, now)
        
        # For non-recurring triggers, we need to check against actual data
        return True  # Will be filtered in _get_matching_rows
    
    def _check_recurring_condition(self, trigger_node: DateBasedTriggerNode, now: datetime) -> bool:
        """Check if a recurring trigger should fire."""
        pattern = trigger_node.recurring_pattern
        
        if not pattern:
            return False
        
        frequency = pattern.get('frequency', 'daily')
        
        if frequency == 'daily':
            # Check if it's time to run daily
            check_time = trigger_node.check_time
            if check_time:
                return now.time() >= check_time
            return True
        
        elif frequency == 'weekly':
            weekday = pattern.get('weekday', 0)  # 0 = Monday
            return now.weekday() == weekday
        
        elif frequency == 'monthly':
            day_of_month = pattern.get('day_of_month', 1)
            return now.day == day_of_month
        
        return False
    
    def _get_matching_rows(self, trigger_node: DateBasedTriggerNode, now: datetime) -> List[Dict]:
        """Get rows that match the date trigger condition."""
        try:
            table = trigger_node.date_field.table
            date_field = trigger_node.date_field
            condition_type = trigger_node.condition_type
            days_offset = trigger_node.days_offset
            
            # Build query based on condition type
            row_handler = RowHandler()
            model = table.get_model()
            
            queryset = model.objects.all()
            
            if condition_type == 'date_reached':
                target_date = now.date()
                queryset = queryset.filter(**{f"{date_field.db_column}__date": target_date})
            
            elif condition_type == 'days_before':
                target_date = now.date() + timedelta(days=days_offset)
                queryset = queryset.filter(**{f"{date_field.db_column}__date": target_date})
            
            elif condition_type == 'days_after':
                target_date = now.date() - timedelta(days=days_offset)
                queryset = queryset.filter(**{f"{date_field.db_column}__date": target_date})
            
            elif condition_type == 'overdue':
                queryset = queryset.filter(**{f"{date_field.db_column}__lt": now})
            
            # Apply additional conditions if specified
            additional_conditions = trigger_node.additional_conditions
            if additional_conditions:
                queryset = self._apply_additional_conditions(queryset, additional_conditions, table)
            
            # Convert to serialized format
            rows = list(queryset[:100])  # Limit to prevent memory issues
            return self._serialize_rows(rows, table)
        
        except Exception as e:
            logger.error(f"Error getting matching rows for date trigger: {e}")
            return []
    
    def _apply_additional_conditions(self, queryset, conditions: Dict, table) -> QuerySet:
        """Apply additional field-based conditions to the queryset."""
        for field_id, condition in conditions.items():
            try:
                field = Field.objects.get(id=field_id, table=table)
                operator = condition.get('operator', 'equals')
                value = condition.get('value')
                
                if operator == 'equals':
                    queryset = queryset.filter(**{field.db_column: value})
                elif operator == 'not_equals':
                    queryset = queryset.exclude(**{field.db_column: value})
                elif operator == 'contains':
                    queryset = queryset.filter(**{f"{field.db_column}__icontains": value})
                # Add more operators as needed
                
            except Field.DoesNotExist:
                continue
        
        return queryset
    
    def _serialize_rows(self, rows: List, table) -> List[Dict]:
        """Serialize rows to the format expected by automation system."""
        from baserow.contrib.database.api.rows.serializers import get_row_serializer_class, RowSerializer
        
        model = table.get_model()
        serializer_class = get_row_serializer_class(model, RowSerializer, is_response=True)
        return serializer_class(rows, many=True).data


class LinkedRecordChangeTriggerServiceType(TriggerServiceTypeMixin, ServiceType):
    """
    Service type for linked record change triggers.
    Monitors changes in related tables through link row fields.
    """
    
    type = "linked_record_change_trigger"
    model_class = LinkedRecordChangeTriggerNode
    returns_list = True
    
    def __init__(self):
        self.on_event = None
        self.connected_signals = []
    
    def start_listening(self, on_event: Callable):
        """Start listening for linked record change events."""
        self.on_event = on_event
        
        # Connect to relevant signals
        from baserow.contrib.database.rows.signals import (
            rows_created, rows_updated, rows_deleted
        )
        
        rows_created.connect(self._handle_linked_record_change)
        rows_updated.connect(self._handle_linked_record_change)
        rows_deleted.connect(self._handle_linked_record_change)
        
        self.connected_signals = [rows_created, rows_updated, rows_deleted]
    
    def stop_listening(self):
        """Stop listening for linked record change events."""
        for signal in self.connected_signals:
            signal.disconnect(self._handle_linked_record_change)
        self.connected_signals = []
        self.on_event = None
    
    def _handle_linked_record_change(self, sender, user, rows, table, model, **kwargs):
        """Handle changes in records that might affect linked record triggers."""
        if not self.on_event:
            return
        
        # Find triggers that monitor this table through link fields
        affected_triggers = self._find_affected_triggers(table)
        
        for trigger_node in affected_triggers:
            try:
                # Check if the change matches the trigger conditions
                if self._change_matches_trigger(trigger_node, rows, kwargs.get('signal_type')):
                    # Get the parent rows that should trigger the automation
                    parent_rows = self._get_parent_rows(trigger_node, rows)
                    
                    if parent_rows:
                        transaction.on_commit(lambda: self.on_event(
                            self.model_class.objects.filter(id=trigger_node.id),
                            parent_rows,
                            user=user
                        ))
            except Exception as e:
                logger.error(f"Error handling linked record change for trigger {trigger_node.id}: {e}")
    
    def _find_affected_triggers(self, changed_table) -> QuerySet:
        """Find trigger nodes that monitor the changed table through link fields."""
        return self.model_class.objects.filter(
            link_field__link_row_table=changed_table,
            workflow__published=True,
            workflow__paused=False
        ).select_related('link_field', 'workflow')
    
    def _change_matches_trigger(self, trigger_node: LinkedRecordChangeTriggerNode, 
                              rows: List, signal_type: str) -> bool:
        """Check if the change matches the trigger's change type."""
        change_type = trigger_node.change_type
        
        if change_type == 'any_change':
            return True
        
        # Map signal types to change types
        signal_mapping = {
            'created': 'linked_record_created',
            'updated': 'linked_record_updated',
            'deleted': 'linked_record_deleted',
        }
        
        return signal_mapping.get(signal_type) == change_type
    
    def _get_parent_rows(self, trigger_node: LinkedRecordChangeTriggerNode, 
                        changed_rows: List) -> List[Dict]:
        """Get the parent rows that should trigger the automation."""
        try:
            link_field = trigger_node.link_field
            parent_table = link_field.table
            
            # Get parent rows that link to the changed rows
            changed_row_ids = [row.id for row in changed_rows]
            
            model = parent_table.get_model()
            queryset = model.objects.filter(
                **{f"{link_field.db_column}__in": changed_row_ids}
            )
            
            # Apply linked record conditions if specified
            conditions = trigger_node.linked_record_conditions
            if conditions:
                queryset = self._apply_additional_conditions(queryset, conditions, parent_table)
            
            rows = list(queryset[:100])
            return self._serialize_rows(rows, parent_table)
        
        except Exception as e:
            logger.error(f"Error getting parent rows for linked record trigger: {e}")
            return []
    
    def _serialize_rows(self, rows: List, table) -> List[Dict]:
        """Serialize rows to the format expected by automation system."""
        from baserow.contrib.database.api.rows.serializers import get_row_serializer_class, RowSerializer
        
        model = table.get_model()
        serializer_class = get_row_serializer_class(model, RowSerializer, is_response=True)
        return serializer_class(rows, many=True).data


class WebhookTriggerServiceType(TriggerServiceTypeMixin, ServiceType):
    """
    Service type for external webhook triggers.
    Provides endpoints for external systems to trigger automations.
    """
    
    type = "webhook_trigger"
    model_class = WebhookTriggerNode
    returns_list = True
    
    def __init__(self):
        self.on_event = None
    
    def start_listening(self, on_event: Callable):
        """Start listening for webhook trigger events."""
        self.on_event = on_event
    
    def stop_listening(self):
        """Stop listening for webhook trigger events."""
        self.on_event = None
    
    def handle_webhook_request(self, webhook_path: str, request_data: Dict, 
                             request_method: str, headers: Dict) -> Dict:
        """Handle incoming webhook requests."""
        try:
            # Find the webhook trigger node
            trigger_node = self.model_class.objects.get(
                webhook_url_path=webhook_path,
                workflow__published=True,
                workflow__paused=False
            )
            
            # Validate the request
            if not self._validate_webhook_request(trigger_node, request_data, request_method, headers):
                return {'error': 'Invalid webhook request', 'status': 401}
            
            # Process the webhook payload
            processed_data = self._process_webhook_payload(trigger_node, request_data)
            
            # Fire the trigger
            if self.on_event:
                self.on_event(
                    self.model_class.objects.filter(id=trigger_node.id),
                    [processed_data],
                    user=None  # External trigger
                )
            
            return {'success': True, 'status': 200}
        
        except self.model_class.DoesNotExist:
            return {'error': 'Webhook not found', 'status': 404}
        except Exception as e:
            logger.error(f"Error handling webhook request: {e}")
            return {'error': 'Internal server error', 'status': 500}
    
    def _validate_webhook_request(self, trigger_node: WebhookTriggerNode, 
                                request_data: Dict, method: str, headers: Dict) -> bool:
        """Validate incoming webhook request."""
        # Check HTTP method
        allowed_methods = trigger_node.allowed_methods
        if allowed_methods and method.upper() not in allowed_methods:
            return False
        
        # Check authentication
        auth_type = trigger_node.auth_type
        
        if auth_type == 'api_key':
            api_key = headers.get('X-API-Key') or request_data.get('api_key')
            return api_key == trigger_node.auth_token
        
        elif auth_type == 'bearer_token':
            auth_header = headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                return token == trigger_node.auth_token
            return False
        
        elif auth_type == 'signature':
            # Implement signature verification
            return self._verify_signature(trigger_node, request_data, headers)
        
        # No authentication required
        return True
    
    def _verify_signature(self, trigger_node: WebhookTriggerNode, 
                         request_data: Dict, headers: Dict) -> bool:
        """Verify webhook signature."""
        import hmac
        import hashlib
        
        signature = headers.get('X-Signature') or headers.get('X-Hub-Signature-256')
        if not signature:
            return False
        
        secret = trigger_node.signature_secret.encode()
        payload = json.dumps(request_data, sort_keys=True).encode()
        
        expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        
        # Compare signatures securely
        return hmac.compare_digest(signature, f"sha256={expected_signature}")
    
    def _process_webhook_payload(self, trigger_node: WebhookTriggerNode, 
                               request_data: Dict) -> Dict:
        """Process webhook payload according to mapping configuration."""
        payload_mapping = trigger_node.payload_mapping
        
        if not payload_mapping:
            return request_data
        
        processed_data = {}
        
        for target_field, source_path in payload_mapping.items():
            try:
                # Extract value from nested path (e.g., "data.user.name")
                value = request_data
                for key in source_path.split('.'):
                    value = value[key]
                processed_data[target_field] = value
            except (KeyError, TypeError):
                # Field not found in payload
                processed_data[target_field] = None
        
        return processed_data


class ConditionalTriggerServiceType(TriggerServiceTypeMixin, ServiceType):
    """
    Service type for conditional triggers.
    Evaluates complex conditions before firing triggers.
    """
    
    type = "conditional_trigger"
    model_class = ConditionalTriggerNode
    returns_list = True
    
    def __init__(self):
        self.on_event = None
    
    def start_listening(self, on_event: Callable):
        """Start listening for conditional trigger events."""
        self.on_event = on_event
        # Conditional triggers are evaluated when their base triggers fire
    
    def stop_listening(self):
        """Stop listening for conditional trigger events."""
        self.on_event = None
    
    def evaluate_conditions(self, trigger_node: ConditionalTriggerNode, 
                          context_data: Dict, rows: List[Dict]) -> bool:
        """Evaluate whether conditions are met for the trigger to fire."""
        try:
            condition_groups = trigger_node.condition_groups
            evaluation_mode = trigger_node.evaluation_mode
            
            if not condition_groups:
                return True  # No conditions means always fire
            
            group_results = []
            
            for group in condition_groups:
                group_result = self._evaluate_condition_group(group, context_data, rows)
                group_results.append(group_result)
            
            # Combine group results based on evaluation mode
            if evaluation_mode == 'all_must_match':
                return all(group_results)
            elif evaluation_mode == 'any_can_match':
                return any(group_results)
            elif evaluation_mode == 'custom_logic':
                return self._evaluate_custom_logic(trigger_node.custom_logic, group_results)
            
            return False
        
        except Exception as e:
            logger.error(f"Error evaluating conditions for trigger {trigger_node.id}: {e}")
            return False
    
    def _evaluate_condition_group(self, group: Dict, context_data: Dict, rows: List[Dict]) -> bool:
        """Evaluate a single condition group."""
        conditions = group.get('conditions', [])
        group_logic = group.get('logic', 'and')  # 'and' or 'or'
        
        condition_results = []
        
        for condition in conditions:
            result = self._evaluate_single_condition(condition, context_data, rows)
            condition_results.append(result)
        
        if group_logic == 'and':
            return all(condition_results)
        else:  # 'or'
            return any(condition_results)
    
    def _evaluate_single_condition(self, condition: Dict, context_data: Dict, rows: List[Dict]) -> bool:
        """Evaluate a single condition."""
        field_name = condition.get('field')
        operator = condition.get('operator')
        expected_value = condition.get('value')
        
        # Get actual value from context or rows
        actual_value = self._get_condition_value(field_name, context_data, rows)
        
        # Evaluate based on operator
        return self._compare_values(actual_value, operator, expected_value)
    
    def _get_condition_value(self, field_name: str, context_data: Dict, rows: List[Dict]) -> Any:
        """Get the value for a condition field from context or rows."""
        # Try context data first
        if field_name in context_data:
            return context_data[field_name]
        
        # Try first row if available
        if rows and field_name in rows[0]:
            return rows[0][field_name]
        
        return None
    
    def _compare_values(self, actual: Any, operator: str, expected: Any) -> bool:
        """Compare values based on the operator."""
        if operator == 'equals':
            return actual == expected
        elif operator == 'not_equals':
            return actual != expected
        elif operator == 'greater_than':
            return actual > expected
        elif operator == 'less_than':
            return actual < expected
        elif operator == 'contains':
            return expected in str(actual) if actual else False
        elif operator == 'is_empty':
            return not actual
        elif operator == 'is_not_empty':
            return bool(actual)
        
        return False
    
    def _evaluate_custom_logic(self, logic_expression: str, group_results: List[bool]) -> bool:
        """Evaluate custom logic expression with group results."""
        try:
            # Replace group IDs with actual results
            expression = logic_expression
            for i, result in enumerate(group_results):
                expression = expression.replace(f"group_{i}", str(result))
            
            # Safely evaluate the expression
            # Note: In production, this should use a safer expression evaluator
            return eval(expression)
        
        except Exception as e:
            logger.error(f"Error evaluating custom logic: {e}")
            return False