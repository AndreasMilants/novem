# Generated by Django 3.0.2 on 2020-01-29 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0005_auto_20200128_2355'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='importantlevelanswer',
            unique_together={('survey_instance', 'level')},
        ),
        migrations.RemoveField(
            model_name='importantlevelanswer',
            name='number',
        ),
    ]