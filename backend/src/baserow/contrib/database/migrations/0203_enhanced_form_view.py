# Generated migration for enhanced form view features

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):
    dependencies = [
        ("database", "0202_people_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="formview",
            name="custom_branding",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Custom branding configuration including logos, colors, and thank-you messages",
            ),
        ),
        migrations.AddField(
            model_name="formview",
            name="access_control",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Access control settings for public and internal form access",
            ),
        ),
        migrations.AddField(
            model_name="formview",
            name="validation_config",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Comprehensive field validation configuration with custom error messages",
            ),
        ),
        migrations.AddField(
            model_name="formview",
            name="shareable_links",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Secure shareable link configurations with access controls",
            ),
        ),
        migrations.AddField(
            model_name="formviewfieldoptions",
            name="conditional_logic",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Advanced conditional field logic for showing/hiding fields based on answers",
            ),
        ),
        migrations.AddField(
            model_name="formviewfieldoptions",
            name="validation_rules",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Custom validation rules with error messages for this field",
            ),
        ),
    ]