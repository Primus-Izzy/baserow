"""
Enhanced trigger node types for the automation system.

This module contains node types for date-based triggers, linked record change triggers,
external webhook triggers, and conditional trigger evaluation.
"""

from typing import Dict, List, Optional

from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet

from baserow.contrib.automation.nodes.registries import AutomationNodeType
from baserow.contrib.automation.nodes.enhanced_trigger_models import (
    DateBasedTriggerNode,
    LinkedRecordChangeTriggerNode,
    WebhookTriggerNode,
    ConditionalTriggerNode,
)
from baserow.contrib.automation.nodes.enhanced_trigger_service_types import (
    DateBasedTriggerServiceType,
    LinkedRecordChangeTriggerServiceType,
    WebhookTriggerServiceType,
    ConditionalTriggerServiceType,
)
from baserow.core.services.models import Service


class EnhancedAutomationNodeTriggerType(AutomationNodeType):
    """Base class for enhanced automation trigger node types."""
    
    is_workflow_trigger = True

    def on_event(
        self,
        service_queryset: QuerySet[Service],
        event_payload: Optional[List[Dict]] = None,
        user: Optional[AbstractUser] = None,
    ):
        """Handle trigger events and run associated workflows."""
        from baserow.contrib.automation.workflows.service import AutomationWorkflowService
        from django.utils import timezone

        workflow_service = AutomationWorkflowService()
        now = timezone.now()

        # Get trigger nodes for the services
        triggers = (
            self.model_class.objects.filter(
                service__in=service_queryset,
            )
            .filter(
                workflow__published=True,
                workflow__paused=False
            )
            .select_related("workflow__automation__workspace")
        )

        for trigger in triggers:
            try:
                workflow = trigger.workflow
                
                # For conditional triggers, evaluate conditions first
                if hasattr(trigger, 'condition_groups') and trigger.condition_groups:
                    service_type = self.get_service_type()
                    if not service_type.evaluate_conditions(trigger, {}, event_payload or []):
                        continue  # Skip this trigger if conditions not met
                
                # Run the workflow
                workflow_service.run_workflow(
                    workflow.id,
                    event_payload,
                    user=user,
                )
                
                # Handle test runs
                if workflow.allow_test_run_until:
                    workflow.allow_test_run_until = None
                    workflow.save(update_fields=["allow_test_run_until"])
                    
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error running workflow for trigger {trigger.id}: {e}")

    def after_register(self):
        """Register the service type and start listening for events."""
        from baserow.core.services.registries import service_type_registry
        
        service_type = service_type_registry.get(self.service_type)
        service_type.start_listening(self.on_event)
        return super().after_register()

    def before_unregister(self):
        """Unregister the service type and stop listening for events."""
        from baserow.core.services.registries import service_type_registry
        
        service_type = service_type_registry.get(self.service_type)
        service_type.stop_listening()
        return super().before_unregister()
    
    def get_service_type(self):
        """Get the associated service type instance."""
        from baserow.core.services.registries import service_type_registry
        return service_type_registry.get(self.service_type)


class DateBasedTriggerNodeType(EnhancedAutomationNodeTriggerType):
    """
    Node type for date-based triggers.
    Handles scheduled triggers, date reached triggers, and recurring patterns.
    """
    
    type = "date_based_trigger"
    model_class = DateBasedTriggerNode
    service_type = DateBasedTriggerServiceType.type
    
    def get_pytest_params(self, pytest_data_fixture) -> Dict[str, int]:
        """Get parameters for pytest fixtures."""
        from baserow.contrib.database.fields.handler import FieldHandler
        
        # Create a test table with a date field
        table = pytest_data_fixture.create_table_for_table()
        date_field = pytest_data_fixture.create_date_field(table=table)
        
        service = pytest_data_fixture.create_service_for_table(
            table=table,
            service_type=self.service_type
        )
        
        return {
            "service": service,
            "date_field": date_field,
            "condition_type": "date_reached",
        }
    
    def export_serialized(self, trigger_node: DateBasedTriggerNode, 
                         files_zip=None, storage=None) -> Dict:
        """Export trigger node configuration."""
        return {
            "id": trigger_node.id,
            "type": self.type,
            "date_field_id": trigger_node.date_field_id,
            "condition_type": trigger_node.condition_type,
            "days_offset": trigger_node.days_offset,
            "recurring_pattern": trigger_node.recurring_pattern,
            "check_time": trigger_node.check_time.isoformat() if trigger_node.check_time else None,
            "additional_conditions": trigger_node.additional_conditions,
        }
    
    def import_serialized(self, workflow, serialized_values: Dict, 
                         id_mapping: Dict, files_zip=None, storage=None) -> DateBasedTriggerNode:
        """Import trigger node from serialized configuration."""
        # Map field ID
        date_field_id = serialized_values.get("date_field_id")
        if date_field_id and date_field_id in id_mapping.get("database_fields", {}):
            serialized_values["date_field_id"] = id_mapping["database_fields"][date_field_id]
        
        return super().import_serialized(workflow, serialized_values, id_mapping, files_zip, storage)


class LinkedRecordChangeTriggerNodeType(EnhancedAutomationNodeTriggerType):
    """
    Node type for linked record change triggers.
    Monitors changes in related tables through link row fields.
    """
    
    type = "linked_record_change_trigger"
    model_class = LinkedRecordChangeTriggerNode
    service_type = LinkedRecordChangeTriggerServiceType.type
    
    def get_pytest_params(self, pytest_data_fixture) -> Dict[str, int]:
        """Get parameters for pytest fixtures."""
        # Create test tables with link relationship
        table1 = pytest_data_fixture.create_table_for_table()
        table2 = pytest_data_fixture.create_table_for_table()
        link_field = pytest_data_fixture.create_link_row_field(
            table=table1, 
            link_row_table=table2
        )
        
        service = pytest_data_fixture.create_service_for_table(
            table=table1,
            service_type=self.service_type
        )
        
        return {
            "service": service,
            "link_field": link_field,
            "change_type": "any_change",
        }
    
    def export_serialized(self, trigger_node: LinkedRecordChangeTriggerNode, 
                         files_zip=None, storage=None) -> Dict:
        """Export trigger node configuration."""
        return {
            "id": trigger_node.id,
            "type": self.type,
            "link_field_id": trigger_node.link_field_id,
            "change_type": trigger_node.change_type,
            "monitored_fields": trigger_node.monitored_fields,
            "linked_record_conditions": trigger_node.linked_record_conditions,
        }
    
    def import_serialized(self, workflow, serialized_values: Dict, 
                         id_mapping: Dict, files_zip=None, storage=None) -> LinkedRecordChangeTriggerNode:
        """Import trigger node from serialized configuration."""
        # Map field ID
        link_field_id = serialized_values.get("link_field_id")
        if link_field_id and link_field_id in id_mapping.get("database_fields", {}):
            serialized_values["link_field_id"] = id_mapping["database_fields"][link_field_id]
        
        return super().import_serialized(workflow, serialized_values, id_mapping, files_zip, storage)


class WebhookTriggerNodeType(EnhancedAutomationNodeTriggerType):
    """
    Node type for external webhook triggers.
    Provides endpoints for external systems to trigger automations.
    """
    
    type = "webhook_trigger"
    model_class = WebhookTriggerNode
    service_type = WebhookTriggerServiceType.type
    
    def get_pytest_params(self, pytest_data_fixture) -> Dict[str, int]:
        """Get parameters for pytest fixtures."""
        import uuid
        
        service = pytest_data_fixture.create_service_for_table(
            service_type=self.service_type
        )
        
        return {
            "service": service,
            "webhook_url_path": f"webhook_{uuid.uuid4().hex[:8]}",
            "auth_type": "api_key",
            "auth_token": "test_token_123",
            "allowed_methods": ["POST"],
        }
    
    def export_serialized(self, trigger_node: WebhookTriggerNode, 
                         files_zip=None, storage=None) -> Dict:
        """Export trigger node configuration."""
        return {
            "id": trigger_node.id,
            "type": self.type,
            "webhook_url_path": trigger_node.webhook_url_path,
            "auth_type": trigger_node.auth_type,
            "auth_token": trigger_node.auth_token,  # Note: In production, encrypt this
            "signature_secret": trigger_node.signature_secret,
            "allowed_methods": trigger_node.allowed_methods,
            "payload_mapping": trigger_node.payload_mapping,
            "validation_rules": trigger_node.validation_rules,
        }
    
    def import_serialized(self, workflow, serialized_values: Dict, 
                         id_mapping: Dict, files_zip=None, storage=None) -> WebhookTriggerNode:
        """Import trigger node from serialized configuration."""
        # Generate new webhook path to avoid conflicts
        import uuid
        serialized_values["webhook_url_path"] = f"webhook_{uuid.uuid4().hex[:8]}"
        
        return super().import_serialized(workflow, serialized_values, id_mapping, files_zip, storage)


class ConditionalTriggerNodeType(EnhancedAutomationNodeTriggerType):
    """
    Node type for conditional triggers.
    Evaluates complex conditions before firing triggers.
    """
    
    type = "conditional_trigger"
    model_class = ConditionalTriggerNode
    service_type = ConditionalTriggerServiceType.type
    
    def get_pytest_params(self, pytest_data_fixture) -> Dict[str, int]:
        """Get parameters for pytest fixtures."""
        # Create a base trigger to extend
        base_trigger = pytest_data_fixture.create_automation_node(
            type="rows_created"
        )
        
        service = pytest_data_fixture.create_service_for_table(
            service_type=self.service_type
        )
        
        return {
            "service": service,
            "base_trigger": base_trigger,
            "evaluation_mode": "all_must_match",
            "condition_groups": [
                {
                    "conditions": [
                        {
                            "field": "status",
                            "operator": "equals",
                            "value": "active"
                        }
                    ],
                    "logic": "and"
                }
            ],
        }
    
    def export_serialized(self, trigger_node: ConditionalTriggerNode, 
                         files_zip=None, storage=None) -> Dict:
        """Export trigger node configuration."""
        return {
            "id": trigger_node.id,
            "type": self.type,
            "base_trigger_id": trigger_node.base_trigger_id,
            "condition_groups": trigger_node.condition_groups,
            "evaluation_mode": trigger_node.evaluation_mode,
            "custom_logic": trigger_node.custom_logic,
            "time_conditions": trigger_node.time_conditions,
        }
    
    def import_serialized(self, workflow, serialized_values: Dict, 
                         id_mapping: Dict, files_zip=None, storage=None) -> ConditionalTriggerNode:
        """Import trigger node from serialized configuration."""
        # Map base trigger ID
        base_trigger_id = serialized_values.get("base_trigger_id")
        if base_trigger_id and base_trigger_id in id_mapping.get("automation_nodes", {}):
            serialized_values["base_trigger_id"] = id_mapping["automation_nodes"][base_trigger_id]
        
        return super().import_serialized(workflow, serialized_values, id_mapping, files_zip, storage)
    
    def on_event(self, service_queryset: QuerySet[Service], 
                event_payload: Optional[List[Dict]] = None, 
                user: Optional[AbstractUser] = None):
        """Override to handle conditional evaluation."""
        # Get conditional triggers
        conditional_triggers = self.model_class.objects.filter(
            service__in=service_queryset,
            workflow__published=True,
            workflow__paused=False
        ).select_related("workflow__automation__workspace", "base_trigger")
        
        for trigger in conditional_triggers:
            try:
                # Evaluate conditions
                service_type = self.get_service_type()
                context_data = {"user_id": user.id if user else None}
                
                if service_type.evaluate_conditions(trigger, context_data, event_payload or []):
                    # Conditions met, fire the base trigger
                    base_trigger_type = trigger.base_trigger.get_type()
                    base_trigger_type.on_event(
                        service_queryset.filter(id=trigger.base_trigger.service_id),
                        event_payload,
                        user
                    )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error evaluating conditional trigger {trigger.id}: {e}")