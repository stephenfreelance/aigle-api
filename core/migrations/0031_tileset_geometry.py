# Generated by Django 5.0.6 on 2024-06-18 07:59

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0030_alter_tileset_tile_set_scheme"),
    ]

    operations = [
        migrations.AddField(
            model_name="tileset",
            name="geometry",
            field=django.contrib.gis.db.models.fields.GeometryField(
                default="POLYGON ((3.8772558254653973 43.61103761205618, 3.8790667534657075 43.61103761205618, 3.8790667534657075 43.61115188932109, 3.8772558254653973 43.61115188932109, 3.8772558254653973 43.61103761205618))",
                srid=4326,
            ),
            preserve_default=False,
        ),
    ]