# Generated by Django 5.0.6 on 2024-05-31 15:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_objecttype"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="objecttype",
            name="display_name",
        ),
    ]
