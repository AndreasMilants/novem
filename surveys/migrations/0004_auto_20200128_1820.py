# Generated by Django 3.0.2 on 2020-01-28 17:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('surveys', '0003_auto_20200128_1700'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='importantlevelanswer',
            options={'verbose_name': 'Important Level Answer', 'verbose_name_plural': 'Important Level Answer'},
        ),
        migrations.AlterModelOptions(
            name='surveyinstance',
            options={'verbose_name': 'Survey Answers', 'verbose_name_plural': 'Survey Answers'},
        ),
        migrations.AlterField(
            model_name='answer',
            name='survey_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys.SurveyInstance', verbose_name='Survey Instance'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterUniqueTogether(
            name='importantlevelanswer',
            unique_together={('survey_instance', 'level')},
        ),
    ]
