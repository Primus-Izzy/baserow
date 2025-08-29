# Generated migration for enhanced dashboard widgets

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_widget_dashboarddatasource_summarywidget'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardLayout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grid_columns', models.IntegerField(default=12, help_text='Number of columns in the grid system')),
                ('grid_row_height', models.IntegerField(default=60, help_text='Height of each grid row in pixels')),
                ('layout_data', models.JSONField(default=list, help_text='Array of widget layout configurations')),
                ('breakpoints', models.JSONField(default=dict, help_text='Responsive breakpoint configurations')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('dashboard', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='layout_config', to='dashboard.dashboard')),
            ],
        ),
        migrations.CreateModel(
            name='KPIWidget',
            fields=[
                ('widget_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dashboard.widget')),
                ('display_format', models.CharField(choices=[('number', 'Number'), ('percentage', 'Percentage'), ('currency', 'Currency'), ('duration', 'Duration')], default='number', help_text='Format for displaying the KPI value', max_length=50)),
                ('prefix_text', models.CharField(blank=True, help_text='Text to display before the value', max_length=50)),
                ('suffix_text', models.CharField(blank=True, help_text='Text to display after the value', max_length=50)),
                ('comparison_enabled', models.BooleanField(default=False, help_text='Whether to show comparison with previous period')),
                ('color_scheme', models.CharField(choices=[('blue', 'Blue'), ('green', 'Green'), ('red', 'Red'), ('orange', 'Orange'), ('purple', 'Purple'), ('custom', 'Custom')], default='blue', max_length=20)),
                ('custom_color', models.CharField(blank=True, help_text='Custom hex color code (e.g., #FF5733)', max_length=7)),
                ('comparison_data_source', models.ForeignKey(blank=True, help_text='Data source for comparison value', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kpi_comparison_widgets', to='dashboard.dashboarddatasource')),
                ('data_source', models.ForeignKey(help_text='Data source for fetching the KPI value.', on_delete=django.db.models.deletion.PROTECT, to='dashboard.dashboarddatasource')),
            ],
            options={
                'ordering': ('order', 'id'),
            },
            bases=('dashboard.widget',),
        ),
        migrations.CreateModel(
            name='EnhancedChartWidget',
            fields=[
                ('widget_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dashboard.widget')),
                ('chart_type', models.CharField(choices=[('bar', 'Bar Chart'), ('line', 'Line Chart'), ('area', 'Area Chart'), ('pie', 'Pie Chart'), ('donut', 'Donut Chart'), ('mixed', 'Mixed Chart')], default='bar', max_length=20)),
                ('layout_config', models.JSONField(default=dict, help_text='Layout configuration for drag-and-drop positioning')),
                ('series_config', models.JSONField(default=list, help_text='Configuration for each data series')),
                ('color_palette', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=7), blank=True, default=list, help_text='Custom color palette for chart series', size=None)),
                ('show_legend', models.BooleanField(default=True)),
                ('show_grid', models.BooleanField(default=True)),
                ('show_tooltips', models.BooleanField(default=True)),
                ('enable_animations', models.BooleanField(default=True)),
                ('animation_duration', models.IntegerField(default=1000, help_text='Animation duration in milliseconds')),
                ('auto_refresh', models.BooleanField(default=False, help_text='Enable automatic data refresh')),
                ('refresh_interval', models.IntegerField(default=60, help_text='Refresh interval in seconds')),
                ('data_sources', models.ManyToManyField(help_text='Multiple data sources for the chart', to='dashboard.dashboarddatasource')),
            ],
            options={
                'ordering': ('order', 'id'),
            },
            bases=('dashboard.widget',),
        ),
        migrations.CreateModel(
            name='WidgetDataAggregation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aggregation_type', models.CharField(choices=[('sum', 'Sum'), ('avg', 'Average'), ('count', 'Count'), ('min', 'Minimum'), ('max', 'Maximum'), ('median', 'Median'), ('std_dev', 'Standard Deviation')], max_length=20)),
                ('field_name', models.CharField(max_length=255)),
                ('group_by_fields', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None)),
                ('cached_result', models.JSONField(default=dict, help_text='Cached aggregation result')),
                ('cache_expires_at', models.DateTimeField(blank=True, help_text='When the cached result expires', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.dashboarddatasource')),
                ('widget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aggregations', to='dashboard.widget')),
            ],
            options={
                'unique_together': {('widget', 'data_source', 'aggregation_type', 'field_name')},
            },
        ),
    ]