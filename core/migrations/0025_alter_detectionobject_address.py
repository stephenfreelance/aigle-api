# Generated by Django 5.0.6 on 2024-06-10 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_detection_deleted_at_detectiondata_deleted_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detectionobject',
            name='address',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
