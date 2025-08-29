"""
Trigger template handler for the automation system.

This module provides functionality to manage and apply trigger templates
for common automation patterns.
"""

import logging
from typing import Dict, List, Optional, Any

from django.db import transaction
from django.contrib.auth.models import AbstractUser

from baserow.contrib.automation.nodes.enhanced_trigger_models import TriggerTemplate
from baserow.contrib.automation.nodes.handler import AutomationNodeHandler
from baserow.contrib.automation.workflows.models import AutomationWorkflow
from baserow.contrib.database.fields.models import Field
from baserow.core.exceptions import UserNotInWorkspace

logger = logging.getLogger(__name__)


class TriggerTemplateHandler:
    """Handler for managing trigger templates and applying them to workflows."""
    
    def get_available_templates(self, table=None, user: Optional[AbstractUser] = None) -> List[Dict]:
        """
        Get available trigger templates, optionally filtered by table compatibility.
        
        :param table: Optional table to filter templates by field type compatibility
        :param user: User requesting templates (for permission checking)
        :return: List of available template configurations
        """
        queryset = TriggerTemplate.objects.filter(is_active=True)
        
        templates = []
        for template in queryset:
            # Check if template is compatible with the table
            if table and not self._is_template_compatible(template, table):
                continue
            
            templates.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'usage_count': template.usage_count,
                'required_field_types': template.required_field_types,
                'preview_config': self._get_template_preview(template),
            })
        
        return templates
    
    def get_templates_by_category(self, category: str) -> List[TriggerTemplate]:
        """Get templates filtered by category."""
        return TriggerTemplate.objects.filter(
            category=category,
            is_active=True
        ).order_by('name')
    
    def apply_template(self, template_id: int, workflow: AutomationWorkflow, 
                      field_mappings: Dict[str, int], user: AbstractUser) -> Dict:
        """
        Apply a trigger template to a workflow.
        
        :param template_id: ID of the template to apply
        :param workflow: Target workflow to add the trigger to
        :param field_mappings: Mapping of template field names to actual field IDs
        :param user: User applying the template
        :return: Dictionary with created nodes and configuration
        """
        try:
            template = TriggerTemplate.objects.get(id=template_id, is_active=True)
        except TriggerTemplate.DoesNotExist:
            raise ValueError(f"Template {template_id} not found or inactive")
        
        # Check user permissions
        if not user.has_perm('automation.change_automationworkflow', workflow):
            raise UserNotInWorkspace("User does not have permission to modify this workflow")
        
        # Validate field mappings
        self._validate_field_mappings(template, field_mappings, workflow.automation.workspace)
        
        with transaction.atomic():
            # Create trigger node from template
            trigger_node = self._create_trigger_from_template(
                template, workflow, field_mappings, user
            )
            
            # Create associated action nodes if specified in template
            action_nodes = self._create_actions_from_template(
                template, workflow, trigger_node, field_mappings, user
            )
            
            # Update template usage count
            template.usage_count += 1
            template.save(update_fields=['usage_count'])
            
            return {
                'trigger_node': trigger_node,
                'action_nodes': action_nodes,
                'template_applied': template.name,
            }
    
    def create_custom_template(self, name: str, description: str, category: str,
                             trigger_config: Dict, action_templates: List[Dict],
                             required_field_types: List[str], user: AbstractUser) -> TriggerTemplate:
        """
        Create a custom trigger template.
        
        :param name: Template name
        :param description: Template description
        :param category: Template category
        :param trigger_config: Trigger configuration
        :param action_templates: List of action template configurations
        :param required_field_types: Required field types for this template
        :param user: User creating the template
        :return: Created template instance
        """
        template = TriggerTemplate.objects.create(
            name=name,
            description=description,
            category=category,
            trigger_config=trigger_config,
            action_templates=action_templates,
            required_field_types=required_field_types,
        )
        
        logger.info(f"Created custom template '{name}' by user {user.id}")
        return template
    
    def get_template_preview(self, template_id: int) -> Dict:
        """Get a preview of what a template will create."""
        try:
            template = TriggerTemplate.objects.get(id=template_id, is_active=True)
            return self._get_template_preview(template)
        except TriggerTemplate.DoesNotExist:
            raise ValueError(f"Template {template_id} not found")
    
    def _is_template_compatible(self, template: TriggerTemplate, table) -> bool:
        """Check if a template is compatible with a table's field types."""
        required_types = template.required_field_types
        if not required_types:
            return True  # No specific requirements
        
        # Get available field types in the table
        available_types = set(
            Field.objects.filter(table=table)
            .values_list('type', flat=True)
            .distinct()
        )
        
        # Check if all required types are available
        return all(field_type in available_types for field_type in required_types)
    
    def _validate_field_mappings(self, template: TriggerTemplate, 
                                field_mappings: Dict[str, int], workspace) -> None:
        """Validate that field mappings are correct and accessible."""
        required_fields = self._extract_required_fields(template.trigger_config)
        
        for field_name in required_fields:
            if field_name not in field_mappings:
                raise ValueError(f"Missing field mapping for '{field_name}'")
            
            field_id = field_mappings[field_name]
            try:
                field = Field.objects.get(
                    id=field_id,
                    table__database__workspace=workspace
                )
                
                # Validate field type if specified in template
                expected_type = required_fields[field_name].get('type')
                if expected_type and field.type != expected_type:
                    raise ValueError(
                        f"Field '{field_name}' must be of type '{expected_type}', "
                        f"got '{field.type}'"
                    )
            except Field.DoesNotExist:
                raise ValueError(f"Field {field_id} not found or not accessible")
    
    def _extract_required_fields(self, trigger_config: Dict) -> Dict[str, Dict]:
        """Extract required field information from trigger configuration."""
        required_fields = {}
        
        # Extract fields based on trigger type
        trigger_type = trigger_config.get('type')
        
        if trigger_type == 'date_based_trigger':
            date_field = trigger_config.get('date_field')
            if date_field:
                required_fields[date_field] = {'type': 'date'}
        
        elif trigger_type == 'linked_record_change_trigger':
            link_field = trigger_config.get('link_field')
            if link_field:
                required_fields[link_field] = {'type': 'link_row'}
        
        # Extract fields from additional conditions
        conditions = trigger_config.get('additional_conditions', {})
        for field_name, condition in conditions.items():
            if field_name not in required_fields:
                required_fields[field_name] = {}
        
        return required_fields
    
    def _create_trigger_from_template(self, template: TriggerTemplate, 
                                    workflow: AutomationWorkflow,
                                    field_mappings: Dict[str, int], 
                                    user: AbstractUser):
        """Create a trigger node from template configuration."""
        trigger_config = template.trigger_config.copy()
        
        # Replace field names with actual field IDs
        self._apply_field_mappings(trigger_config, field_mappings)
        
        # Create the trigger node
        node_handler = AutomationNodeHandler()
        trigger_type = trigger_config.pop('type')
        
        return node_handler.create_node(
            trigger_type,
            workflow=workflow,
            **trigger_config
        )
    
    def _create_actions_from_template(self, template: TriggerTemplate,
                                    workflow: AutomationWorkflow,
                                    trigger_node,
                                    field_mappings: Dict[str, int],
                                    user: AbstractUser) -> List:
        """Create action nodes from template action configurations."""
        action_nodes = []
        
        for action_template in template.action_templates:
            action_config = action_template.copy()
            
            # Replace field names with actual field IDs
            self._apply_field_mappings(action_config, field_mappings)
            
            # Create the action node
            node_handler = AutomationNodeHandler()
            action_type = action_config.pop('type')
            
            action_node = node_handler.create_node(
                action_type,
                workflow=workflow,
                previous_node=trigger_node,
                **action_config
            )
            
            action_nodes.append(action_node)
        
        return action_nodes
    
    def _apply_field_mappings(self, config: Dict, field_mappings: Dict[str, int]) -> None:
        """Apply field mappings to a configuration dictionary."""
        for key, value in config.items():
            if key.endswith('_field') and isinstance(value, str):
                # Replace field name with field ID
                if value in field_mappings:
                    config[key] = field_mappings[value]
            elif isinstance(value, dict):
                # Recursively apply to nested dictionaries
                self._apply_field_mappings(value, field_mappings)
            elif isinstance(value, list):
                # Apply to list items if they are dictionaries
                for item in value:
                    if isinstance(item, dict):
                        self._apply_field_mappings(item, field_mappings)
    
    def _get_template_preview(self, template: TriggerTemplate) -> Dict:
        """Generate a preview of what the template will create."""
        return {
            'trigger_type': template.trigger_config.get('type'),
            'trigger_description': self._describe_trigger_config(template.trigger_config),
            'action_count': len(template.action_templates),
            'action_descriptions': [
                self._describe_action_config(action)
                for action in template.action_templates
            ],
            'estimated_complexity': self._estimate_template_complexity(template),
        }
    
    def _describe_trigger_config(self, config: Dict) -> str:
        """Generate a human-readable description of trigger configuration."""
        trigger_type = config.get('type')
        
        if trigger_type == 'date_based_trigger':
            condition = config.get('condition_type', 'date_reached')
            return f"Triggers when {condition.replace('_', ' ')}"
        
        elif trigger_type == 'linked_record_change_trigger':
            change_type = config.get('change_type', 'any_change')
            return f"Triggers on {change_type.replace('_', ' ')} in linked records"
        
        elif trigger_type == 'webhook_trigger':
            return "Triggers when external webhook is received"
        
        elif trigger_type == 'conditional_trigger':
            return "Triggers when complex conditions are met"
        
        return f"Triggers on {trigger_type.replace('_', ' ')}"
    
    def _describe_action_config(self, config: Dict) -> str:
        """Generate a human-readable description of action configuration."""
        action_type = config.get('type')
        
        if action_type == 'create_row':
            return "Creates a new row"
        elif action_type == 'update_row':
            return "Updates existing row"
        elif action_type == 'smtp_email':
            return "Sends email notification"
        elif action_type == 'http_request':
            return "Makes HTTP request to external service"
        
        return f"Performs {action_type.replace('_', ' ')}"
    
    def _estimate_template_complexity(self, template: TriggerTemplate) -> str:
        """Estimate the complexity of a template."""
        complexity_score = 0
        
        # Base complexity from trigger type
        trigger_type = template.trigger_config.get('type')
        if trigger_type in ['conditional_trigger', 'linked_record_change_trigger']:
            complexity_score += 2
        else:
            complexity_score += 1
        
        # Add complexity for actions
        complexity_score += len(template.action_templates)
        
        # Add complexity for conditions
        conditions = template.trigger_config.get('additional_conditions', {})
        complexity_score += len(conditions)
        
        if complexity_score <= 2:
            return 'Simple'
        elif complexity_score <= 5:
            return 'Medium'
        else:
            return 'Complex'


def get_default_templates() -> List[Dict]:
    """Get default trigger templates that should be available in all installations."""
    return [
        {
            'name': 'Due Date Reminder',
            'description': 'Send email reminders when tasks are due soon',
            'category': 'project_management',
            'trigger_config': {
                'type': 'date_based_trigger',
                'date_field': 'due_date',
                'condition_type': 'days_before',
                'days_offset': 1,
                'additional_conditions': {
                    'status': {
                        'operator': 'not_equals',
                        'value': 'completed'
                    }
                }
            },
            'action_templates': [
                {
                    'type': 'smtp_email',
                    'to_field': 'assigned_to',
                    'subject': 'Task Due Tomorrow: {name}',
                    'body': 'Your task "{name}" is due tomorrow ({due_date}). Please complete it on time.'
                }
            ],
            'required_field_types': ['date', 'email', 'single_select']
        },
        {
            'name': 'New Task Assignment',
            'description': 'Notify users when they are assigned to a new task',
            'category': 'notifications',
            'trigger_config': {
                'type': 'rows_created',
                'additional_conditions': {
                    'assigned_to': {
                        'operator': 'is_not_empty',
                        'value': None
                    }
                }
            },
            'action_templates': [
                {
                    'type': 'smtp_email',
                    'to_field': 'assigned_to',
                    'subject': 'New Task Assigned: {name}',
                    'body': 'You have been assigned a new task: "{name}". Description: {description}'
                }
            ],
            'required_field_types': ['email', 'text']
        },
        {
            'name': 'Status Change Notification',
            'description': 'Notify team when task status changes to completed',
            'category': 'notifications',
            'trigger_config': {
                'type': 'rows_updated',
                'additional_conditions': {
                    'status': {
                        'operator': 'equals',
                        'value': 'completed'
                    }
                }
            },
            'action_templates': [
                {
                    'type': 'http_request',
                    'url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
                    'method': 'POST',
                    'body': {
                        'text': 'Task completed: {name} by {assigned_to}'
                    }
                }
            ],
            'required_field_types': ['single_select', 'email']
        },
        {
            'name': 'Overdue Task Alert',
            'description': 'Daily alert for overdue tasks',
            'category': 'project_management',
            'trigger_config': {
                'type': 'date_based_trigger',
                'date_field': 'due_date',
                'condition_type': 'overdue',
                'recurring_pattern': {
                    'frequency': 'daily'
                },
                'check_time': '09:00:00',
                'additional_conditions': {
                    'status': {
                        'operator': 'not_equals',
                        'value': 'completed'
                    }
                }
            },
            'action_templates': [
                {
                    'type': 'smtp_email',
                    'to_field': 'assigned_to',
                    'subject': 'Overdue Task Alert: {name}',
                    'body': 'Your task "{name}" was due on {due_date} and is now overdue. Please complete it as soon as possible.'
                }
            ],
            'required_field_types': ['date', 'email', 'single_select']
        },
        {
            'name': 'Weekly Status Report',
            'description': 'Generate weekly status reports',
            'category': 'reporting',
            'trigger_config': {
                'type': 'date_based_trigger',
                'date_field': 'created_on',
                'condition_type': 'recurring',
                'recurring_pattern': {
                    'frequency': 'weekly',
                    'weekday': 4  # Friday
                },
                'check_time': '17:00:00'
            },
            'action_templates': [
                {
                    'type': 'aggregate_rows',
                    'aggregation_type': 'count',
                    'group_by_field': 'status'
                },
                {
                    'type': 'smtp_email',
                    'to': 'manager@company.com',
                    'subject': 'Weekly Status Report',
                    'body': 'Weekly task summary: {aggregation_result}'
                }
            ],
            'required_field_types': ['date', 'single_select']
        }
    ]