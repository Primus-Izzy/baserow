# Generated migration for ProgressBarField

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("database", "0200_calendar_view"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProgressBarField",
            fields=[
                (
                    "field_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="database.field",
                    ),
                ),
                (
                    "source_type",
                    models.CharField(
                        choices=[
                            ("manual", "Manual input"),
                            ("field", "Numeric field"),
                            ("formula", "Formula calculation"),
                        ],
                        default="manual",
                        help_text="Source type for progress calculation",
                        max_length=20,
                    ),
                ),
                (
                    "source_field",
                    models.ForeignKey(
                        blank=True,
                        help_text="Source field for progress calculation (when source_type is 'field')",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="database.field",
                    ),
                ),
                (
                    "source_formula",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Formula expression for progress calculation (when source_type is 'formula')",
                    ),
                ),
                (
                    "min_value",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        help_text="Minimum value for progress calculation",
                        max_digits=10,
                    ),
                ),
                (
                    "max_value",
                    models.DecimalField(
                        decimal_places=2,
                        default=100,
                        help_text="Maximum value for progress calculation",
                        max_digits=10,
                    ),
                ),
                (
                    "show_percentage",
                    models.BooleanField(
                        default=True,
                        help_text="Whether to show percentage text on the progress bar",
                    ),
                ),
                (
                    "color_scheme",
                    models.CharField(
                        choices=[
                            ("default", "Default (blue)"),
                            ("success", "Success (green)"),
                            ("warning", "Warning (yellow)"),
                            ("danger", "Danger (red)"),
                            ("custom", "Custom colors"),
                        ],
                        default="default",
                        help_text="Color scheme for the progress bar",
                        max_length=20,
                    ),
                ),
                (
                    "custom_color_start",
                    models.CharField(
                        blank=True,
                        default="#3b82f6",
                        help_text="Start color for custom gradient (hex format)",
                        max_length=7,
                    ),
                ),
                (
                    "custom_color_end",
                    models.CharField(
                        blank=True,
                        default="#1d4ed8",
                        help_text="End color for custom gradient (hex format)",
                        max_length=7,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("database.field",),
        ),
    ]