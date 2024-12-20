# Generated by Django 5.0.6 on 2024-10-01 14:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0066_detectionobject_comment_alter_parcel_id_parcellaire"),
    ]

    operations = [
        migrations.AddField(
            model_name="usergroup",
            name="custom_geo_zones",
            field=models.ManyToManyField(
                related_name="user_groups_custom_geo_zones", to="core.geocustomzone"
            ),
        ),
    ]
