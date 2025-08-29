# Generated migration for People field type

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0201_progress_bar_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeopleField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='database.field')),
                ('multiple_people', models.BooleanField(default=False, help_text='Whether multiple people can be selected for this field')),
                ('notify_when_added', models.BooleanField(default=True, help_text='Whether to notify users when they are added to this field')),
                ('notify_when_removed', models.BooleanField(default=False, help_text='Whether to notify users when they are removed from this field')),
                ('people_default', models.JSONField(blank=True, help_text='Default user IDs for this field. Can be None, user IDs, or 0 for current user', null=True)),
                ('show_avatar', models.BooleanField(default=True, help_text='Whether to show user avatars in the field display')),
                ('show_email', models.BooleanField(default=False, help_text='Whether to show user email addresses in the field display')),
            ],
            options={
                'abstract': False,
            },
            bases=('database.field',),
        ),
    ]