# Generated migration for collaboration models

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('database', '0196_enhanced_grid_view'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPresence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('web_socket_id', models.CharField(max_length=255)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('cursor_position', models.JSONField(blank=True, default=dict)),
                ('is_typing', models.BooleanField(default=False)),
                ('typing_field_id', models.PositiveIntegerField(blank=True, null=True)),
                ('typing_row_id', models.PositiveIntegerField(blank=True, null=True)),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.table')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('view', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='database.view')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['table', 'view'], name='database_us_table_i_b8c123_idx'),
                    models.Index(fields=['last_seen'], name='database_us_last_se_4f8a9c_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='CollaborationSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_id', models.PositiveIntegerField()),
                ('field_id', models.PositiveIntegerField()),
                ('web_socket_id', models.CharField(max_length=255)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('lock_data', models.JSONField(blank=True, default=dict)),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.table')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['table', 'row_id'], name='database_co_table_i_8f2a1b_idx'),
                    models.Index(fields=['last_activity'], name='database_co_last_ac_9c3d4e_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_id', models.PositiveIntegerField()),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_resolved', models.BooleanField(default=False)),
                ('mentions', models.ManyToManyField(blank=True, related_name='mentioned_in_comments', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='database.comment')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.table')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
                'indexes': [
                    models.Index(fields=['table', 'row_id'], name='database_co_table_i_5a6b7c_idx'),
                    models.Index(fields=['created_at'], name='database_co_created_8d9e0f_idx'),
                    models.Index(fields=['parent'], name='database_co_parent__1a2b3c_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('row_created', 'Row Created'), ('row_updated', 'Row Updated'), ('row_deleted', 'Row Deleted'), ('field_created', 'Field Created'), ('field_updated', 'Field Updated'), ('field_deleted', 'Field Deleted'), ('view_created', 'View Created'), ('view_updated', 'View Updated'), ('view_deleted', 'View Deleted'), ('comment_created', 'Comment Created'), ('comment_updated', 'Comment Updated'), ('comment_deleted', 'Comment Deleted'), ('user_joined', 'User Joined'), ('user_left', 'User Left')], max_length=50)),
                ('details', models.JSONField(blank=True, default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.table')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['table', 'timestamp'], name='database_ac_table_i_4d5e6f_idx'),
                    models.Index(fields=['user', 'timestamp'], name='database_ac_user_id_7g8h9i_idx'),
                    models.Index(fields=['action_type', 'timestamp'], name='database_ac_action__0j1k2l_idx'),
                ],
            },
        ),
        migrations.AlterUniqueTogether(
            name='userpresence',
            unique_together={('user', 'table', 'view', 'web_socket_id')},
        ),
        migrations.AlterUniqueTogether(
            name='collaborationsession',
            unique_together={('table', 'row_id', 'field_id')},
        ),
    ]