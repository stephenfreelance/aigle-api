# Generated by Django 5.0.6 on 2024-07-24 13:20

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0059_rename_core_detect_uuid_ecc8f4_idx_detection_uuid_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="last_position",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, null=True, srid=4326
            ),
        ),
    ]