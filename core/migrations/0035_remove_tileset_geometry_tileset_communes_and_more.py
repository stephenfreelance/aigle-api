# Generated by Django 5.0.6 on 2024-06-27 13:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0034_alter_tileset_geometry"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tileset",
            name="geometry",
        ),
        migrations.AddField(
            model_name="tileset",
            name="communes",
            field=models.ManyToManyField(
                related_name="tile_sets", to="core.geocommune"
            ),
        ),
        migrations.AddField(
            model_name="tileset",
            name="departments",
            field=models.ManyToManyField(
                related_name="tile_sets", to="core.geodepartment"
            ),
        ),
        migrations.AddField(
            model_name="tileset",
            name="regions",
            field=models.ManyToManyField(related_name="tile_sets", to="core.georegion"),
        ),
    ]
