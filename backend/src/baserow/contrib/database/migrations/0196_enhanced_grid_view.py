# Generated manually for enhanced grid view features

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('database', '0195_alter_pendingsearchvalueupdate_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gridview',
            name='sticky_header',
            field=models.BooleanField(default=True, help_text='Whether column headers should remain visible during vertical scrolling'),
        ),
        migrations.AddField(
            model_name='gridview',
            name='conditional_formatting',
            field=models.JSONField(blank=True, default=list, help_text='Rules for conditional formatting with color-coding based on field values'),
        ),
        migrations.AddField(
            model_name='gridview',
            name='column_groups',
            field=models.JSONField(blank=True, default=list, help_text='Configuration for column grouping with collapsible/expandable groups'),
        ),
        migrations.AddField(
            model_name='gridview',
            name='filter_presets',
            field=models.JSONField(blank=True, default=list, help_text='Saved filter configurations for quick reuse'),
        ),
        migrations.AddField(
            model_name='gridviewfieldoptions',
            name='inline_editing_config',
            field=models.JSONField(blank=True, default=dict, help_text='Configuration for enhanced inline editing including rich text, dropdowns, and input types'),
        ),
        migrations.CreateModel(
            name='GridViewConditionalFormatting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the conditional formatting rule', max_length=255)),
                ('condition_type', models.CharField(help_text='Type of condition (equals, contains, greater_than, etc.)', max_length=50)),
                ('condition_value', models.TextField(help_text='Value to compare against')),
                ('background_color', models.CharField(blank=True, help_text='Background color in hex format (e.g., #FF0000)', max_length=7)),
                ('text_color', models.CharField(blank=True, help_text='Text color in hex format (e.g., #FFFFFF)', max_length=7)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this rule is active')),
                ('order', models.PositiveIntegerField(default=0, help_text='Order of rule application')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('field', models.ForeignKey(help_text='Field to apply the condition to', on_delete=django.db.models.deletion.CASCADE, to='database.field')),
                ('grid_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditional_formatting_rules', to='database.gridview')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='GridViewFilterPreset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the filter preset', max_length=255)),
                ('filters', models.JSONField(help_text='Saved filter configuration')),
                ('is_default', models.BooleanField(default=False, help_text='Whether this is the default preset')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(help_text='User who created this preset', on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('grid_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filter_presets', to='database.gridview')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='GridViewColumnGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the column group', max_length=255)),
                ('is_collapsed', models.BooleanField(default=False, help_text='Whether the group is collapsed')),
                ('order', models.PositiveIntegerField(default=0, help_text='Order of the group')),
                ('color', models.CharField(blank=True, help_text='Group header color in hex format', max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fields', models.ManyToManyField(help_text='Fields included in this group', to='database.field')),
                ('grid_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='column_groups', to='database.gridview')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='gridviewconditionalformatting',
            unique_together={('grid_view', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='gridviewfilterpreset',
            unique_together={('grid_view', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='gridviewcolumngroup',
            unique_together={('grid_view', 'name')},
        ),
    ]