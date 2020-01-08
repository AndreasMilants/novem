# Generated by Django 3.0.2 on 2020-01-08 12:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, unique=True, verbose_name='name')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_active', models.BooleanField(default=True, help_text='Users can register with this organisation', verbose_name='is active')),
            ],
            options={
                'verbose_name': 'Organisation',
                'verbose_name_plural': 'Organisations',
            },
        ),
        migrations.CreateModel(
            name='OrganisationUserLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organisation', to='organisations.Organisation', verbose_name='organisation')),
            ],
        ),
    ]
