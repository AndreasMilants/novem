# Generated by Django 3.0.2 on 2020-01-29 22:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0004_auto_20200129_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='section',
            name='name',
            field=models.CharField(max_length=63, verbose_name='Name'),
        ),
    ]
