# Generated by Django 3.0.2 on 2020-01-11 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0002_auto_20200110_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='slug',
            field=models.SlugField(default='t'),
        ),
    ]