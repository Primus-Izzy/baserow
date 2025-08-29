"""
Action template handler for managing common automation workflow patterns.

This module provides functionality to create, manage, and apply action templates
that encapsulate common automation patterns.
"""

from typing import Dict, List, Any, Optional
from django.contrib.auth.models import AbstractUser
from django.db import transaction

from baserow.contrib.automation.nodes.enhanced_action_models import ActionTemplate
from baserow.contrib.automation.nodes.handler import AutomationNodeHandler
from baserow.contrib.automation.workflows.models import AutomationWorkflow


class ActionTemplateHandler:
    """
    Handler for managing action templates and applying them to workflows.
    """
    
    def create_template(
        self,
        name: str,
        description: str,
        category: str,
        template_config: Dict[str, Any],
        required_fields: List[str],
        user: Optional[AbstractUser] = None,
        is_system_template: bool = False
    ) -> ActionTemplate:
        """
        Create a new action template.
        
        :param name: Display name for the template
        :param description: Description of what the template does
        :param category: Template category
        :param template_config: Configuration template
        :param required_fields: List of required field configurations
        :param user: User creating the template
        :param is_system_template: Whether this is a system template
        :return: Created ActionTemplate instance
        """
        
        template = ActionTemplate.objects.create(
            name=name,
            description=description,
            category=category,
            template_config=template_config,
            required_fields=required_fields,
            created_by=user,
            is_system_template=is_system_template
        )
        
        return template
    
    def get_templates_by_category(self, category: str) -> List[ActionTemplate]:
        """
        Get all templates in a specific category.
        
        :param category: Template category to filter by
        :return: List of ActionTemplate instances
        """
        
        return list(
            ActionTemplate.objects.filter(category=category)
            .order_by('-usage_count', 'name')
        )
    
    def get_popular_templates(self, limit: int = 10) -> List[ActionTemplate]:
        """
        Get the most popular templates based on usage count.
        
        :param limit: Maximum number of templates to return
        :return: List of ActionTemplate instances
        """
        
        return list(
            ActionTemplate.objects.order_by('-usage_count', 'name')[:limit]
        )
    
    def apply_template(
        self,
        template: ActionTemplate,
        workflow: AutomationWorkflow,
        configuration_overrides: Dict[str, Any],
        user: AbstractUser
    ) -> List[Any]:  # Returns list of created nodes
        """
        Apply a template to a workflow, creating the necessary nodes.
        
        :param template: Template to apply
        :param workflow: Workflow to add nodes to
        :param configuration_overrides: User-provided configuration values
        :param user: User applying the template
        :return: List of created automation nodes
        """
        
        # Validate required fields are provided
        self._validate_required_fields(template, configuration_overrides)
        
        # Merge template config with user overrides
        final_config = self._merge_configurations(
            template.template_config, 
            configuration_overrides
        )
        
        created_nodes = []
        
        with transaction.atomic():
            # Create nodes based on template configuration
            for node_config in final_config.get('nodes', []):
                node = self._create_node_from_config(
                    workflow, node_config, user
                )
                created_nodes.append(node)
            
            # Increment usage count
            template.usage_count += 1
            template.save(update_fields=['usage_count'])
        
        return created_nodes
    
    def _validate_required_fields(
        self, 
        template: ActionTemplate, 
        configuration: Dict[str, Any]
    ):
        """
        Validate that all required fields are provided in the configuration.
        
        :param template: Template being applied
        :param configuration: User-provided configuration
        :raises ValueError: If required fields are missing
        """
        
        missing_fields = []
        
        for field_name in template.required_fields:
            if field_name not in configuration:
                missing_fields.append(field_name)
        
        if missing_fields:
            raise ValueError(
                f"Missing required fields for template '{template.name}': "
                f"{', '.join(missing_fields)}"
            )
    
    def _merge_configurations(
        self, 
        template_config: Dict[str, Any], 
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge template configuration with user overrides.
        
        :param template_config: Base template configuration
        :param overrides: User-provided overrides
        :return: Merged configuration
        """
        
        # Deep merge configurations
        merged = template_config.copy()
        
        def deep_merge(base: Dict, override: Dict):
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        
        deep_merge(merged, overrides)
        return merged
    
    def _create_node_from_config(
        self,
        workflow: AutomationWorkflow,
        node_config: Dict[str, Any],
        user: AbstractUser
    ):
        """
        Create an automation node from configuration.
        
        :param workflow: Workflow to add the node to
        :param node_config: Node configuration
        :param user: User creating the node
        :return: Created automation node
        """
        
        # This would use the AutomationNodeHandler to create nodes
        # For now, return a placeholder
        
        node_handler = AutomationNodeHandler()
        
        # Extract node type and configuration
        node_type = node_config.get('type')
        service_config = node_config.get('service', {})
        
        # Create the node (simplified implementation)
        # In a real implementation, this would properly create the service
        # and node based on the configuration
        
        return {
            'type': node_type,
            'config': service_config,
            'workflow_id': workflow.id
        }
    
    def create_system_templates(self):
        """
        Create built-in system templates for common automation patterns.
        """
        
        templates = [
            {
                'name': 'Send Welcome Email',
                'description': 'Send a welcome email when a new user is added',
                'category': 'notification',
                'template_config': {
                    'nodes': [
                        {
                            'type': 'notification',
                            'service': {
                                'notification_type': 'email',
                                'subject_template': 'Welcome to {{ workspace_name }}!',
                                'message_template': 'Hello {{ user_name }}, welcome to our workspace!',
                            }
                        }
                    ]
                },
                'required_fields': ['workspace_name', 'user_email']
            },
            {
                'name': 'Status Change Notification',
                'description': 'Notify team when task status changes to completed',
                'category': 'notification',
                'template_config': {
                    'nodes': [
                        {
                            'type': 'conditional_branch',
                            'service': {
                                'condition_template': '{{ status }}',
                                'condition_type': 'equals',
                                'comparison_value_template': 'completed'
                            }
                        },
                        {
                            'type': 'notification',
                            'service': {
                                'notification_type': 'slack',
                                'subject_template': 'Task Completed',
                                'message_template': 'Task "{{ task_name }}" has been completed by {{ user_name }}',
                            }
                        }
                    ]
                },
                'required_fields': ['slack_webhook_url', 'task_name_field']
            },
            {
                'name': 'Deadline Reminder',
                'description': 'Send reminder notifications before task deadlines',
                'category': 'notification',
                'template_config': {
                    'nodes': [
                        {
                            'type': 'delay',
                            'service': {
                                'delay_type': 'until_date',
                                'delay_until_template': '{{ deadline_date }}'
                            }
                        },
                        {
                            'type': 'notification',
                            'service': {
                                'notification_type': 'email',
                                'subject_template': 'Deadline Reminder: {{ task_name }}',
                                'message_template': 'Your task "{{ task_name }}" is due on {{ deadline_date }}',
                            }
                        }
                    ]
                },
                'required_fields': ['deadline_field', 'assignee_field']
            },
            {
                'name': 'Data Sync Webhook',
                'description': 'Sync data changes to external system via webhook',
                'category': 'integration',
                'template_config': {
                    'nodes': [
                        {
                            'type': 'webhook',
                            'service': {
                                'method': 'POST',
                                'payload_template': '{"id": {{ row_id }}, "data": {{ row_data }}, "action": "{{ action }}"}',
                                'headers': {
                                    'Content-Type': 'application/json'
                                }
                            }
                        }
                    ]
                },
                'required_fields': ['webhook_url', 'api_key']
            },
            {
                'name': 'Approval Workflow',
                'description': 'Route items for approval based on value thresholds',
                'category': 'workflow_control',
                'template_config': {
                    'nodes': [
                        {
                            'type': 'conditional_branch',
                            'service': {
                                'condition_template': '{{ amount }}',
                                'condition_type': 'greater_than',
                                'comparison_value_template': '{{ approval_threshold }}'
                            }
                        },
                        {
                            'type': 'status_change',
                            'service': {
                                'new_value_template': 'pending_approval',
                                'condition_template': 'true'
                            }
                        },
                        {
                            'type': 'notification',
                            'service': {
                                'notification_type': 'email',
                                'subject_template': 'Approval Required: {{ item_name }}',
                                'message_template': 'Item "{{ item_name }}" requires approval (Amount: {{ amount }})',
                            }
                        }
                    ]
                },
                'required_fields': ['amount_field', 'approval_threshold', 'status_field', 'approver_email']
            }
        ]
        
        for template_data in templates:
            # Check if template already exists
            existing = ActionTemplate.objects.filter(
                name=template_data['name'],
                is_system_template=True
            ).first()
            
            if not existing:
                self.create_template(
                    name=template_data['name'],
                    description=template_data['description'],
                    category=template_data['category'],
                    template_config=template_data['template_config'],
                    required_fields=template_data['required_fields'],
                    is_system_template=True
                )
    
    def get_template_by_id(self, template_id: int) -> ActionTemplate:
        """
        Get a template by its ID.
        
        :param template_id: Template ID
        :return: ActionTemplate instance
        :raises ActionTemplate.DoesNotExist: If template not found
        """
        
        return ActionTemplate.objects.get(id=template_id)
    
    def delete_template(self, template_id: int, user: AbstractUser):
        """
        Delete a template (only if user has permission).
        
        :param template_id: Template ID to delete
        :param user: User requesting deletion
        :raises PermissionError: If user doesn't have permission
        """
        
        template = self.get_template_by_id(template_id)
        
        # Check permissions
        if template.is_system_template:
            raise PermissionError("Cannot delete system templates")
        
        if template.created_by != user:
            raise PermissionError("Can only delete templates you created")
        
        template.delete()
    
    def update_template(
        self,
        template_id: int,
        user: AbstractUser,
        **updates
    ) -> ActionTemplate:
        """
        Update a template (only if user has permission).
        
        :param template_id: Template ID to update
        :param user: User requesting update
        :param updates: Fields to update
        :return: Updated ActionTemplate instance
        :raises PermissionError: If user doesn't have permission
        """
        
        template = self.get_template_by_id(template_id)
        
        # Check permissions
        if template.is_system_template:
            raise PermissionError("Cannot modify system templates")
        
        if template.created_by != user:
            raise PermissionError("Can only modify templates you created")
        
        # Update allowed fields
        allowed_fields = [
            'name', 'description', 'category', 
            'template_config', 'required_fields'
        ]
        
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(template, field, value)
        
        template.save()
        return template