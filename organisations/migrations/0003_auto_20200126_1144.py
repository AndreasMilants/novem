# Generated by Django 3.0.2 on 2020-01-26 10:44

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0002_auto_20200126_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='parent_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='child_section', to='organisations.Section', verbose_name='parent_section'),
        ),
        migrations.AlterField(
            model_name='section',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]