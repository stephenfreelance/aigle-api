# Generated by Django 5.0.6 on 2024-07-22 09:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0057_geocustomzone_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="geocustomzone",
            name="geo_custom_zone_status",
            field=models.CharField(
                choices=[("ACTIVE", "ACTIVE"), ("INACTIVE", "INACTIVE")],
                default="ACTIVE",
                max_length=255,
            ),
        ),
    ]
