# Generated by Django 5.1.2 on 2024-11-07 17:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('has_db', models.BooleanField()),
                ('has_www', models.BooleanField()),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitor.site')),
            ],
            options={
                'unique_together': {('site', 'date')},
            },
        ),
    ]
