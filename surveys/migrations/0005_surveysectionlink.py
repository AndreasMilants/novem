# Generated by Django 3.0.2 on 2020-01-17 10:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0002_auto_20200117_1100'),
        ('surveys', '0004_auto_20200114_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveySectionLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organisations.Section', verbose_name='section')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.Survey', verbose_name='survey')),
            ],
            options={
                'verbose_name': 'Survey-section-link',
                'verbose_name_plural': 'Survey-section-links',
            },
        ),
    ]
