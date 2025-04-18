# Generated by Django 5.1.2 on 2025-02-10 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='db_arch_template',
            field=models.CharField(default='{name}_{date}.sql', max_length=100),
        ),
        migrations.AddField(
            model_name='site',
            name='files_arch_template',
            field=models.CharField(default='{name}_{date}.tar.gz', max_length=100),
        ),
        migrations.AddField(
            model_name='site',
            name='has_db',
            field=models.BooleanField(default=False),
        ),
    ]
