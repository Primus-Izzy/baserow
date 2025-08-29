"""
Enhanced form view handler for advanced form features including conditional logic,
custom branding, access controls, and validation.
"""

import secrets
import uuid
from typing import Dict, List, Any, Optional
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from baserow.contrib.database.views.models import FormView, FormViewFieldOptions
from baserow.contrib.database.fields.models import Field
from baserow.core.exceptions import UserNotInWorkspace


class EnhancedFormHandler:
    """
    Handler for enhanced form view features including conditional logic,
    custom branding, access controls, and validation.
    """

    def update_custom_branding(
        self, user: User, form_view: FormView, branding_config: Dict[str, Any]
    ) -> FormView:
        """
        Update custom branding configuration for a form view.
        
        :param user: The user making the request
        :param form_view: The form view to update
        :param branding_config: Branding configuration including logos, colors, etc.
        :return: Updated form view
        """
        # Validate branding configuration
        self._validate_branding_config(branding_config)
        
        form_view.custom_branding = branding_config
        form_view.save(update_fields=["custom_branding"])
        
        return form_view

    def update_access_control(
        self, user: User, form_view: FormView, access_config: Dict[str, Any]
    ) -> FormView:
        """
        Update access control settings for a form view.
        
        :param user: The user making the request
        :param form_view: The form view to update
        :param access_config: Access control configuration
        :return: Updated form view
        """
        # Validate access control configuration
        self._validate_access_control_config(access_config)
        
        form_view.access_control = access_config
        form_view.save(update_fields=["access_control"])
        
        return form_view

    def update_validation_config(
        self, user: User, form_view: FormView, validation_config: Dict[str, Any]
    ) -> FormView:
        """
        Update validation configuration for a form view.
        
        :param user: The user making the request
        :param form_view: The form view to update
        :param validation_config: Validation configuration
        :return: Updated form view
        """
        # Validate validation configuration
        self._validate_validation_config(validation_config)
        
        form_view.validation_config = validation_config
        form_view.save(update_fields=["validation_config"])
        
        return form_view

    def create_shareable_link(
        self, user: User, form_view: FormView, link_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new shareable link for a form view.
        
        :param user: The user creating the link
        :param form_view: The form view to create a link for
        :param link_config: Link configuration including access controls
        :return: Created link configuration with generated URL
        """
        # Generate unique link ID and token
        link_id = str(uuid.uuid4())
        link_token = secrets.token_urlsafe(32)
        
        # Create link configuration
        link = {
            "id": link_id,
            "token": link_token,
            "name": link_config.get("name", "Untitled Link"),
            "description": link_config.get("description", ""),
            "access_type": link_config.get("access_type", "public"),
            "expires_at": link_config.get("expires_at"),
            "max_submissions": link_config.get("max_submissions"),
            "current_submissions": 0,
            "is_active": link_config.get("is_active", True),
            "created_by": user.id,
            "created_at": timezone.now().isoformat(),
            "permissions": link_config.get("permissions", {}),
        }
        
        # Add to form view's shareable links
        current_links = form_view.shareable_links or []
        current_links.append(link)
        form_view.shareable_links = current_links
        form_view.save(update_fields=["shareable_links"])
        
        return link

    def update_shareable_link(
        self, user: User, form_view: FormView, link_id: str, link_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing shareable link.
        
        :param user: The user updating the link
        :param form_view: The form view containing the link
        :param link_id: ID of the link to update
        :param link_config: Updated link configuration
        :return: Updated link configuration
        """
        current_links = form_view.shareable_links or []
        
        for i, link in enumerate(current_links):
            if link.get("id") == link_id:
                # Update link configuration
                link.update(link_config)
                link["updated_at"] = timezone.now().isoformat()
                current_links[i] = link
                
                form_view.shareable_links = current_links
                form_view.save(update_fields=["shareable_links"])
                
                return link
        
        raise ValueError(f"Shareable link with ID {link_id} not found")

    def delete_shareable_link(
        self, user: User, form_view: FormView, link_id: str
    ) -> None:
        """
        Delete a shareable link.
        
        :param user: The user deleting the link
        :param form_view: The form view containing the link
        :param link_id: ID of the link to delete
        """
        current_links = form_view.shareable_links or []
        
        for i, link in enumerate(current_links):
            if link.get("id") == link_id:
                current_links.pop(i)
                form_view.shareable_links = current_links
                form_view.save(update_fields=["shareable_links"])
                return
        
        raise ValueError(f"Shareable link with ID {link_id} not found")

    def update_field_conditional_logic(
        self, user: User, field_options: FormViewFieldOptions, logic_config: Dict[str, Any]
    ) -> FormViewFieldOptions:
        """
        Update conditional logic for a form field.
        
        :param user: The user making the request
        :param field_options: The field options to update
        :param logic_config: Conditional logic configuration
        :return: Updated field options
        """
        # Validate conditional logic configuration
        self._validate_conditional_logic_config(logic_config)
        
        field_options.conditional_logic = logic_config
        field_options.save(update_fields=["conditional_logic"])
        
        return field_options

    def update_field_validation_rules(
        self, user: User, field_options: FormViewFieldOptions, validation_rules: List[Dict[str, Any]]
    ) -> FormViewFieldOptions:
        """
        Update validation rules for a form field.
        
        :param user: The user making the request
        :param field_options: The field options to update
        :param validation_rules: List of validation rules
        :return: Updated field options
        """
        # Validate validation rules
        self._validate_field_validation_rules(validation_rules)
        
        field_options.validation_rules = validation_rules
        field_options.save(update_fields=["validation_rules"])
        
        return field_options

    def evaluate_conditional_logic(
        self, field_options: FormViewFieldOptions, form_data: Dict[str, Any]
    ) -> bool:
        """
        Evaluate whether a field should be shown based on conditional logic.
        
        :param field_options: The field options containing conditional logic
        :param form_data: Current form data to evaluate against
        :return: True if field should be shown, False otherwise
        """
        logic_config = field_options.conditional_logic
        
        if not logic_config or not logic_config.get("enabled", False):
            return True
        
        conditions = logic_config.get("conditions", [])
        if not conditions:
            return True
        
        logic_type = logic_config.get("logic_type", "AND")
        
        results = []
        for condition in conditions:
            result = self._evaluate_condition(condition, form_data)
            results.append(result)
        
        if logic_type == "AND":
            return all(results)
        elif logic_type == "OR":
            return any(results)
        else:
            return True

    def validate_field_value(
        self, field_options: FormViewFieldOptions, value: Any
    ) -> List[str]:
        """
        Validate a field value against custom validation rules.
        
        :param field_options: The field options containing validation rules
        :param value: The value to validate
        :return: List of validation error messages
        """
        errors = []
        validation_rules = field_options.validation_rules or []
        
        for rule in validation_rules:
            if not self._validate_rule(rule, value):
                error_message = rule.get("error_message", "Validation failed")
                errors.append(error_message)
        
        return errors

    def _validate_branding_config(self, config: Dict[str, Any]) -> None:
        """Validate branding configuration."""
        allowed_keys = {
            "logo_url", "logo_alt", "primary_color", "secondary_color",
            "background_color", "text_color", "thank_you_title",
            "thank_you_message", "custom_css"
        }
        
        for key in config.keys():
            if key not in allowed_keys:
                raise ValidationError(f"Invalid branding configuration key: {key}")

    def _validate_access_control_config(self, config: Dict[str, Any]) -> None:
        """Validate access control configuration."""
        allowed_keys = {
            "public_access", "require_authentication", "allowed_domains",
            "ip_restrictions", "submission_limit", "time_restrictions"
        }
        
        for key in config.keys():
            if key not in allowed_keys:
                raise ValidationError(f"Invalid access control configuration key: {key}")

    def _validate_validation_config(self, config: Dict[str, Any]) -> None:
        """Validate validation configuration."""
        allowed_keys = {
            "global_rules", "field_rules", "custom_messages"
        }
        
        for key in config.keys():
            if key not in allowed_keys:
                raise ValidationError(f"Invalid validation configuration key: {key}")

    def _validate_conditional_logic_config(self, config: Dict[str, Any]) -> None:
        """Validate conditional logic configuration."""
        required_keys = {"enabled"}
        allowed_keys = {
            "enabled", "logic_type", "conditions", "show_when_true"
        }
        
        for key in required_keys:
            if key not in config:
                raise ValidationError(f"Missing required conditional logic key: {key}")
        
        for key in config.keys():
            if key not in allowed_keys:
                raise ValidationError(f"Invalid conditional logic configuration key: {key}")

    def _validate_field_validation_rules(self, rules: List[Dict[str, Any]]) -> None:
        """Validate field validation rules."""
        for rule in rules:
            required_keys = {"type", "error_message"}
            for key in required_keys:
                if key not in rule:
                    raise ValidationError(f"Missing required validation rule key: {key}")

    def _evaluate_condition(self, condition: Dict[str, Any], form_data: Dict[str, Any]) -> bool:
        """Evaluate a single condition against form data."""
        field_id = condition.get("field_id")
        operator = condition.get("operator")
        expected_value = condition.get("value")
        
        if field_id not in form_data:
            return False
        
        actual_value = form_data[field_id]
        
        if operator == "equals":
            return actual_value == expected_value
        elif operator == "not_equals":
            return actual_value != expected_value
        elif operator == "contains":
            return str(expected_value).lower() in str(actual_value).lower()
        elif operator == "not_contains":
            return str(expected_value).lower() not in str(actual_value).lower()
        elif operator == "is_empty":
            return not actual_value
        elif operator == "is_not_empty":
            return bool(actual_value)
        elif operator == "greater_than":
            try:
                return float(actual_value) > float(expected_value)
            except (ValueError, TypeError):
                return False
        elif operator == "less_than":
            try:
                return float(actual_value) < float(expected_value)
            except (ValueError, TypeError):
                return False
        
        return False

    def _validate_rule(self, rule: Dict[str, Any], value: Any) -> bool:
        """Validate a value against a single validation rule."""
        rule_type = rule.get("type")
        
        if rule_type == "required":
            return bool(value)
        elif rule_type == "min_length":
            min_length = rule.get("value", 0)
            return len(str(value)) >= min_length
        elif rule_type == "max_length":
            max_length = rule.get("value", 0)
            return len(str(value)) <= max_length
        elif rule_type == "pattern":
            import re
            pattern = rule.get("value", "")
            return bool(re.match(pattern, str(value)))
        elif rule_type == "email":
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(email_pattern, str(value)))
        elif rule_type == "url":
            import re
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            return bool(re.match(url_pattern, str(value)))
        elif rule_type == "numeric":
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False
        elif rule_type == "min_value":
            try:
                return float(value) >= float(rule.get("value", 0))
            except (ValueError, TypeError):
                return False
        elif rule_type == "max_value":
            try:
                return float(value) <= float(rule.get("value", 0))
            except (ValueError, TypeError):
                return False
        
        return True