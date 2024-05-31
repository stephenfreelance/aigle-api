from core.models.geo_region import GeoRegion
from core.serializers import UuidTimestampedModelSerializerMixin
from core.serializers.geo_department import GeoDepartmentSerializer

from rest_framework import serializers


class GeoRegionSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = GeoRegion
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "name",
            "display_name",
            "code",
            "surface_km2"
        ]

    code = serializers.CharField(source="insee_code")
    
class GeoRegionDetailSerializer(GeoRegionSerializer):
    class Meta(GeoRegionSerializer.Meta):
        fields = GeoRegionSerializer.Meta.fields + [
            'departments'
        ]
    
    departments = GeoDepartmentSerializer(many=True, read_only=True)