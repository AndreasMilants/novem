# Generated by Django 2.2.7 on 2020-01-07 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]
