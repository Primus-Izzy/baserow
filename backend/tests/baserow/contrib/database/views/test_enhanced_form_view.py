"""
Tests for enhanced form view features including conditional logic,
custom branding, access controls, and validation.
"""

import pytest
from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from baserow.contrib.database.views.models import FormView, FormViewFieldOptions
from baserow.contrib.database.views.enhanced_form_handler import EnhancedFormHandler
from baserow.contrib.database.fields.models import TextField, NumberField
from baserow.core.models import Workspace
from baserow.contrib.database.models import Database, Table


class EnhancedFormHandlerTestCase(TestCase):
    """Test cases for the EnhancedFormHandler class."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.database = Database.objects.create(
            workspace=self.workspace, name="Test Database"
        )
        self.table = Table.objects.create(database=self.database, name="Test Table")
        self.form_view = FormView.objects.create(
            table=self.table, name="Test Form", order=1
        )
        self.text_field = TextField.objects.create(
            table=self.table, name="Text Field", order=1
        )
        self.number_field = NumberField.objects.create(
            table=self.table, name="Number Field", order=2
        )
        self.handler = EnhancedFormHandler()

    def test_update_custom_branding(self):
        """Test updating custom branding configuration."""
        branding_config = {
            "logo_url": "https://example.com/logo.png",
            "logo_alt": "Company Logo",
            "primary_color": "#007bff",
            "secondary_color": "#6c757d",
            "background_color": "#ffffff",
            "text_color": "#212529",
            "thank_you_title": "Thank You!",
            "thank_you_message": "Your submission has been received.",
        }

        updated_view = self.handler.update_custom_branding(
            self.user, self.form_view, branding_config
        )

        self.assertEqual(updated_view.custom_branding, branding_config)
        self.form_view.refresh_from_db()
        self.assertEqual(self.form_view.custom_branding, branding_config)

    def test_update_access_control(self):
        """Test updating access control settings."""
        access_config = {
            "public_access": True,
            "require_authentication": False,
            "submission_limit": 100,
            "allowed_domains": ["example.com"],
        }

        updated_view = self.handler.update_access_control(
            self.user, self.form_view, access_config
        )

        self.assertEqual(updated_view.access_control, access_config)
        self.form_view.refresh_from_db()
        self.assertEqual(self.form_view.access_control, access_config)

    def test_update_validation_config(self):
        """Test updating validation configuration."""
        validation_config = {
            "global_rules": [
                {"type": "required", "message": "This field is required"}
            ],
            "field_rules": {
                str(self.text_field.id): [
                    {"type": "min_length", "value": 5, "message": "Too short"}
                ]
            },
        }

        updated_view = self.handler.update_validation_config(
            self.user, self.form_view, validation_config
        )

        self.assertEqual(updated_view.validation_config, validation_config)
        self.form_view.refresh_from_db()
        self.assertEqual(self.form_view.validation_config, validation_config)

    def test_create_shareable_link(self):
        """Test creating a shareable link."""
        link_config = {
            "name": "Test Link",
            "description": "A test shareable link",
            "access_type": "public",
            "max_submissions": 50,
            "is_active": True,
        }

        created_link = self.handler.create_shareable_link(
            self.user, self.form_view, link_config
        )

        self.assertIn("id", created_link)
        self.assertIn("token", created_link)
        self.assertEqual(created_link["name"], "Test Link")
        self.assertEqual(created_link["access_type"], "public")
        self.assertEqual(created_link["max_submissions"], 50)
        self.assertEqual(created_link["current_submissions"], 0)
        self.assertTrue(created_link["is_active"])

        self.form_view.refresh_from_db()
        self.assertEqual(len(self.form_view.shareable_links), 1)

    def test_update_shareable_link(self):
        """Test updating an existing shareable link."""
        # First create a link
        link_config = {"name": "Original Link", "access_type": "public"}
        created_link = self.handler.create_shareable_link(
            self.user, self.form_view, link_config
        )
        link_id = created_link["id"]

        # Update the link
        update_config = {"name": "Updated Link", "access_type": "private"}
        updated_link = self.handler.update_shareable_link(
            self.user, self.form_view, link_id, update_config
        )

        self.assertEqual(updated_link["name"], "Updated Link")
        self.assertEqual(updated_link["access_type"], "private")

    def test_delete_shareable_link(self):
        """Test deleting a shareable link."""
        # First create a link
        link_config = {"name": "Test Link", "access_type": "public"}
        created_link = self.handler.create_shareable_link(
            self.user, self.form_view, link_config
        )
        link_id = created_link["id"]

        # Delete the link
        self.handler.delete_shareable_link(self.user, self.form_view, link_id)

        self.form_view.refresh_from_db()
        self.assertEqual(len(self.form_view.shareable_links), 0)

    def test_update_field_conditional_logic(self):
        """Test updating conditional logic for a form field."""
        field_options = FormViewFieldOptions.objects.create(
            form_view=self.form_view, field=self.text_field, enabled=True
        )

        logic_config = {
            "enabled": True,
            "logic_type": "AND",
            "show_when_true": True,
            "conditions": [
                {
                    "field_id": self.number_field.id,
                    "operator": "greater_than",
                    "value": 10,
                }
            ],
        }

        updated_options = self.handler.update_field_conditional_logic(
            self.user, field_options, logic_config
        )

        self.assertEqual(updated_options.conditional_logic, logic_config)
        field_options.refresh_from_db()
        self.assertEqual(field_options.conditional_logic, logic_config)

    def test_update_field_validation_rules(self):
        """Test updating validation rules for a form field."""
        field_options = FormViewFieldOptions.objects.create(
            form_view=self.form_view, field=self.text_field, enabled=True
        )

        validation_rules = [
            {"type": "required", "error_message": "This field is required"},
            {"type": "min_length", "value": 5, "error_message": "Too short"},
        ]

        updated_options = self.handler.update_field_validation_rules(
            self.user, field_options, validation_rules
        )

        self.assertEqual(updated_options.validation_rules, validation_rules)
        field_options.refresh_from_db()
        self.assertEqual(field_options.validation_rules, validation_rules)

    def test_evaluate_conditional_logic_and_condition(self):
        """Test evaluating conditional logic with AND condition."""
        field_options = FormViewFieldOptions.objects.create(
            form_view=self.form_view,
            field=self.text_field,
            enabled=True,
            conditional_logic={
                "enabled": True,
                "logic_type": "AND",
                "show_when_true": True,
                "conditions": [
                    {
                        "field_id": self.number_field.id,
                        "operator": "greater_than",
                        "value": 10,
                    }
                ],
            },
        )

        # Test with condition met
        form_data = {self.number_field.id: 15}
        result = self.handler.evaluate_conditional_logic(field_options, form_data)
        self.assertTrue(result)

        # Test with condition not met
        form_data = {self.number_field.id: 5}
        result = self.handler.evaluate_conditional_logic(field_options, form_data)
        self.assertFalse(result)

    def test_evaluate_conditional_logic_or_condition(self):
        """Test evaluating conditional logic with OR condition."""
        field_options = FormViewFieldOptions.objects.create(
            form_view=self.form_view,
            field=self.text_field,
            enabled=True,
            conditional_logic={
                "enabled": True,
                "logic_type": "OR",
                "show_when_true": True,
                "conditions": [
                    {
                        "field_id": self.number_field.id,
                        "operator": "greater_than",
                        "value": 10,
                    },
                    {
                        "field_id": self.number_field.id,
                        "operator": "equals",
                        "value": 5,
                    },
                ],
            },
        )

        # Test with first condition met
        form_data = {self.number_field.id: 15}
        result = self.handler.evaluate_conditional_logic(field_options, form_data)
        self.assertTrue(result)

        # Test with second condition met
        form_data = {self.number_field.id: 5}
        result = self.handler.evaluate_conditional_logic(field_options, form_data)
        self.assertTrue(result)

        # Test with no conditions met
        form_data = {self.number_field.id: 8}
        result = self.handler.evaluate_conditional_logic(field_options, form_data)
        self.assertFalse(result)

    def test_validate_field_value_required(self):
        """Test validating required field value."""
        field_options = FormViewFieldOptions.objects.create(
            form_view=self.form_view,
            field=self.text_field,
            enabled=True,
            validation_rules=[
                {"type": "required", "error_message": "This field is required"}
            ],
        )

        # Test with empty value
        errors = self.handler.validate_field_value(field_options, "")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], "This field is required")

        # Test with valid value
        errors = self.handler.validate_field_value(field_options, "Valid text")
        self.assertEqual(len(errors), 0)

    def test_validate_field_value_min_length(self):
        """Test validating minimum length field value."""
        field_options = FormViewFieldOptions.objects.create(
            form_view=self.form_view,
            field=self.text_field,
            enabled=True,
            validation_rules=[
                {
                    "type": "min_length",
                    "value": 5,
                    "error_message": "Must be at least 5 characters",
                }
            ],
        )

        # Test with short value
        errors = self.handler.validate_field_value(field_options, "Hi")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], "Must be at least 5 characters")

        # Test with valid value
        errors = self.handler.validate_field_value(field_options, "Hello World")
        self.assertEqual(len(errors), 0)

    def test_validate_field_value_email(self):
        """Test validating email field value."""
        field_options = FormViewFieldOptions.objects.create(
            form_view=self.form_view,
            field=self.text_field,
            enabled=True,
            validation_rules=[
                {"type": "email", "error_message": "Invalid email address"}
            ],
        )

        # Test with invalid email
        errors = self.handler.validate_field_value(field_options, "invalid-email")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], "Invalid email address")

        # Test with valid email
        errors = self.handler.validate_field_value(
            field_options, "test@example.com"
        )
        self.assertEqual(len(errors), 0)


class EnhancedFormViewAPITestCase(APITestCase):
    """Test cases for the enhanced form view API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.database = Database.objects.create(
            workspace=self.workspace, name="Test Database"
        )
        self.table = Table.objects.create(database=self.database, name="Test Table")
        self.form_view = FormView.objects.create(
            table=self.table, name="Test Form", order=1
        )
        self.text_field = TextField.objects.create(
            table=self.table, name="Text Field", order=1
        )

        # Add user to workspace
        self.workspace.users.add(self.user)
        self.client.force_authenticate(user=self.user)

    def test_update_custom_branding_api(self):
        """Test the custom branding API endpoint."""
        url = f"/api/database/views/form/{self.form_view.id}/custom-branding/"
        data = {
            "logo_url": "https://example.com/logo.png",
            "primary_color": "#007bff",
            "thank_you_title": "Thank You!",
        }

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.form_view.refresh_from_db()
        self.assertEqual(self.form_view.custom_branding["logo_url"], data["logo_url"])
        self.assertEqual(
            self.form_view.custom_branding["primary_color"], data["primary_color"]
        )

    def test_update_access_control_api(self):
        """Test the access control API endpoint."""
        url = f"/api/database/views/form/{self.form_view.id}/access-control/"
        data = {
            "public_access": True,
            "require_authentication": False,
            "submission_limit": 100,
        }

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.form_view.refresh_from_db()
        self.assertEqual(
            self.form_view.access_control["public_access"], data["public_access"]
        )
        self.assertEqual(
            self.form_view.access_control["submission_limit"], data["submission_limit"]
        )

    def test_update_validation_config_api(self):
        """Test the validation config API endpoint."""
        url = f"/api/database/views/form/{self.form_view.id}/validation-config/"
        data = {
            "global_rules": [
                {"type": "required", "message": "This field is required"}
            ]
        }

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.form_view.refresh_from_db()
        self.assertEqual(
            self.form_view.validation_config["global_rules"], data["global_rules"]
        )

    def test_create_shareable_link_api(self):
        """Test creating a shareable link via API."""
        url = f"/api/database/views/form/{self.form_view.id}/shareable-links/"
        data = {
            "name": "Test Link",
            "description": "A test link",
            "access_type": "public",
            "max_submissions": 50,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_data = response.json()
        self.assertIn("id", response_data)
        self.assertIn("token", response_data)
        self.assertEqual(response_data["name"], data["name"])

    def test_list_shareable_links_api(self):
        """Test listing shareable links via API."""
        # First create a link
        create_url = f"/api/database/views/form/{self.form_view.id}/shareable-links/"
        create_data = {"name": "Test Link", "access_type": "public"}
        self.client.post(create_url, create_data, format="json")

        # List links
        list_url = f"/api/database/views/form/{self.form_view.id}/shareable-links/"
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["name"], "Test Link")

    def test_update_field_options_api(self):
        """Test updating field options via API."""
        field_options = FormViewFieldOptions.objects.create(
            form_view=self.form_view, field=self.text_field, enabled=True
        )

        url = f"/api/database/views/form/{self.form_view.id}/field-options/{self.text_field.id}/"
        data = {
            "conditional_logic": {
                "enabled": True,
                "logic_type": "AND",
                "conditions": [],
            },
            "validation_rules": [
                {"type": "required", "error_message": "This field is required"}
            ],
        }

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        field_options.refresh_from_db()
        self.assertTrue(field_options.conditional_logic["enabled"])
        self.assertEqual(len(field_options.validation_rules), 1)

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access enhanced form endpoints."""
        self.client.force_authenticate(user=None)

        url = f"/api/database/views/form/{self.form_view.id}/custom-branding/"
        response = self.client.patch(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_view_id(self):
        """Test handling of invalid view IDs."""
        url = "/api/database/views/form/99999/custom-branding/"
        response = self.client.patch(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)