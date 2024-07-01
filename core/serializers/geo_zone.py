from core.models.geo_zone import GeoZone
from core.serializers import UuidTimestampedModelSerializerMixin


class GeoZoneSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = GeoZone
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "name",
        ]


class GeoZoneDetailSerializer(GeoZoneSerializer):
    class Meta(GeoZoneSerializer.Meta):
        fields = GeoZoneSerializer.Meta.fields + ["geometry"]
