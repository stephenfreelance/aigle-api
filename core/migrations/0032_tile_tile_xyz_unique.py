# Generated by Django 5.0.6 on 2024-06-18 14:08

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0031_tileset_geometry"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "x",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(0)]
                    ),
                ),
                (
                    "y",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(0)]
                    ),
                ),
                (
                    "z",
                    models.IntegerField(
                        default=19,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "geometry",
                    django.contrib.gis.db.models.fields.GeometryField(srid=4326),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="tile",
            constraint=models.UniqueConstraint(
                fields=("x", "y", "z"), name="xyz_unique"
            ),
        ),
    ]