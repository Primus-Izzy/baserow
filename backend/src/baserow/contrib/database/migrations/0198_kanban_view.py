# Generated manually for Kanban view implementation

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0197_collaboration_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='KanbanView',
            fields=[
                ('view_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='database.view')),
                ('card_configuration', models.JSONField(blank=True, default=dict, help_text='Configuration for card display including visible fields and colors.')),
                ('column_configuration', models.JSONField(blank=True, default=dict, help_text='Configuration for column display and behavior.')),
                ('card_cover_image_field', models.ForeignKey(blank=True, help_text='References a file field of which the first image must be shown as card cover image.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kanban_view_card_cover_image_field', to='database.field')),
                ('single_select_field', models.ForeignKey(blank=True, help_text='References a single select field that determines the Kanban columns.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kanban_view_single_select_field', to='database.field')),
                ('stack_by_field', models.ForeignKey(blank=True, help_text='Field used to stack cards in columns (typically a single select field).', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kanban_view_stack_by_field', to='database.field')),
            ],
            options={
                'abstract': False,
            },
            bases=('database.view',),
        ),
        migrations.CreateModel(
            name='KanbanViewFieldOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hidden', models.BooleanField(default=True, help_text='Whether or not the field should be hidden on the card.')),
                ('order', models.SmallIntegerField(default=32767, help_text='The order that the field has on the card. Lower value is first.')),
                ('show_in_card', models.BooleanField(default=False, help_text='Whether the field should be visible on the card.')),
                ('card_display_style', models.CharField(default='default', help_text='How the field should be displayed on the card (default, compact, badge).', max_length=50)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.field')),
                ('kanban_view', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.kanbanview')),
            ],
            options={
                'ordering': ('order', 'field_id'),
            },
        ),
        migrations.AddField(
            model_name='kanbanview',
            name='field_options',
            field=models.ManyToManyField(through='database.KanbanViewFieldOptions', to='database.field'),
        ),
        migrations.AlterUniqueTogether(
            name='kanbanviewfieldoptions',
            unique_together={('kanban_view', 'field')},
        ),
    ]