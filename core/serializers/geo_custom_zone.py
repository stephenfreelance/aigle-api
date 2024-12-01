from core.models.geo_custom_zone import GeoCustomZone, GeoCustomZoneStatus
from core.serializers import UuidTimestampedModelSerializerMixin
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class GeoCustomZoneGeoFeatureSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = GeoCustomZone
        geo_field = "geometry"
        fields = [
            "uuid",
            "name",
            "color",
            "geo_custom_zone_status",
        ]


class GeoCustomZoneSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = GeoCustomZone
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "name",
            "color",
            "geo_custom_zone_status",
        ]

    def update(self, *args, **kwargs):
        instance = super().update(*args, **kwargs)

        if not instance.geometry:
            instance.geo_custom_zone_status = GeoCustomZoneStatus.INACTIVE
            instance.save()

        return instance

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        if not instance.geometry:
            instance.geo_custom_zone_status = GeoCustomZoneStatus.INACTIVE
            instance.save()

        return instance


class GeoCustomZoneDetailSerializer(GeoCustomZoneSerializer):
    class Meta(GeoCustomZoneSerializer.Meta):
        fields = GeoCustomZoneSerializer.Meta.fields + ["geometry"]
