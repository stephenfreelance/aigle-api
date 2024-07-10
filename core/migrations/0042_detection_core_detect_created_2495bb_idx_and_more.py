# Generated by Django 5.0.6 on 2024-07-09 07:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0041_tileset_max_zoom_tileset_min_zoom_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="detection",
            index=models.Index(
                fields=["created_at"], name="core_detect_created_2495bb_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="detection",
            index=models.Index(fields=["uuid"], name="core_detect_uuid_ecc8f4_idx"),
        ),
        migrations.AddIndex(
            model_name="detection",
            index=models.Index(
                fields=["detection_source"], name="core_detect_detecti_88fc62_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="detection",
            index=models.Index(
                fields=["detection_object", "detection_data"],
                name="core_detect_detecti_5b4111_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="tileset",
            index=models.Index(
                fields=["tile_set_status"], name="core_tilese_tile_se_0de645_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="tileset",
            index=models.Index(
                fields=["tile_set_type"], name="core_tilese_tile_se_efc33c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="tileset",
            index=models.Index(fields=["date"], name="core_tilese_date_70beb9_idx"),
        ),
    ]