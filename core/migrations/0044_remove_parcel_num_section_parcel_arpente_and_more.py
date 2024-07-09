# Generated by Django 5.0.6 on 2024-07-09 12:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0043_parcel"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="parcel",
            name="num_section",
        ),
        migrations.AddField(
            model_name="parcel",
            name="arpente",
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="parcel",
            name="contenance",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="parcel",
            name="prefix",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="parcel",
            name="section",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="parcel",
            name="num_parcel",
            field=models.CharField(max_length=255),
        ),
    ]
