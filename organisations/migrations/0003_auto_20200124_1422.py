# Generated by Django 3.0.2 on 2020-01-24 13:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organisations', '0002_auto_20200117_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisationuserlink',
            name='organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organisations.Organisation', verbose_name='organisation'),
        ),
        migrations.AlterField(
            model_name='section',
            name='organisation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organisations.Organisation', verbose_name='organisation'),
        ),
        migrations.AlterField(
            model_name='section',
            name='parent_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_section', to='organisations.Section', verbose_name='parent_section'),
        ),
        migrations.AlterField(
            model_name='sectionuserlink',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.CreateModel(
            name='SectionAdministrator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organisations.Section', verbose_name='section')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'Section Administrator',
                'verbose_name_plural': 'Section Administrators',
            },
        ),
    ]
