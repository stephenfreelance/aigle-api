# Generated by Django 5.0.6 on 2024-10-30 10:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0073_geocustomzone_geo_custom_zone_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicaldetection",
            name="changed_fields",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historicaldetectiondata",
            name="changed_fields",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historicaldetectionobject",
            name="changed_fields",
            field=models.JSONField(blank=True, null=True),
        ),
    ]