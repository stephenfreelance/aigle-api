# Generated by Django 5.0.6 on 2024-07-09 13:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0045_alter_parcel_id_parcellaire"),
    ]

    operations = [
        migrations.AddField(
            model_name="detectionobject",
            name="parcel",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="detection_objects",
                to="core.parcel",
            ),
        ),
        migrations.AddIndex(
            model_name="parcel",
            index=models.Index(
                fields=["section", "num_parcel", "commune"],
                name="core_parcel_section_24bdea_idx",
            ),
        ),
    ]
