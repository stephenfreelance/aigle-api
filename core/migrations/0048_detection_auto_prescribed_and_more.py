# Generated by Django 5.0.6 on 2024-07-12 13:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0047_detection_core_detect_score_48a965_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="detection",
            name="auto_prescribed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="detectiondata",
            name="detection_prescription_status",
            field=models.CharField(
                choices=[
                    ("PRESCRIBED", "PRESCRIBED"),
                    ("NOT_PRESCRIBED", "NOT_PRESCRIBED"),
                ],
                max_length=255,
                null=True,
            ),
        ),
    ]
