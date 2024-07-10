# Generated by Django 5.0.6 on 2024-07-08 16:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_alter_detectiondata_detection_control_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tileset',
            name='max_zoom',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='tileset',
            name='min_zoom',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='detection',
            name='detection_source',
            field=models.CharField(choices=[('INTERFACE_DRAWN', 'INTERFACE_DRAWN'), ('ANALYSIS', 'ANALYSIS')], default='INTERFACE_DRAWN', max_length=255),
        ),
        migrations.AlterField(
            model_name='detection',
            name='score',
            field=models.FloatField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]