from core.contants.order_by import GEO_CUSTOM_ZONES_ORDER_BYS
from core.models.detection_object import DetectionObject
from core.models.geo_custom_zone import GeoCustomZone, GeoCustomZoneStatus
from core.models.parcel import Parcel
from core.serializers import UuidTimestampedModelSerializerMixin
from core.serializers.detection import DetectionWithTileSerializer
from core.serializers.geo_commune import GeoCommuneSerializer
from core.serializers.detection_object import DetectionObjectMinimalSerializer

from rest_framework import serializers

from core.serializers.geo_custom_zone import GeoCustomZoneSerializer


class ParcelMinimalSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = Parcel
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "id_parcellaire",
            "prefix",
            "section",
            "num_parcel",
            "commune",
        ]

    commune = GeoCommuneSerializer(read_only=True)


class ParcelSerializer(ParcelMinimalSerializer):
    class Meta(ParcelMinimalSerializer.Meta):
        fields = ParcelMinimalSerializer.Meta.fields + [
            "geometry",
        ]


class ParcelDetectionObjectSerializer(DetectionObjectMinimalSerializer):
    class Meta(DetectionObjectMinimalSerializer.Meta):
        fields = DetectionObjectMinimalSerializer.Meta.fields + [
            "detection",
        ]

    detection = serializers.SerializerMethodField()

    def get_detection(self, obj: DetectionObject):
        if self.context.get("tile_set_uuid"):
            detection = obj.detections.filter(
                tile_set__uuid=self.context["tile_set_uuid"]
            ).first()
        else:
            detection = obj.detections.order_by("-tile_set__date").first()

        if not detection:
            return None

        detection_serialized = DetectionWithTileSerializer(detection)
        return detection_serialized.data


class ParcelDetailSerializer(ParcelSerializer):
    class Meta(ParcelSerializer.Meta):
        fields = ParcelSerializer.Meta.fields + [
            "detection_objects",
            "custom_geo_zones",
        ]

    detection_objects = ParcelDetectionObjectSerializer(many=True)
    custom_geo_zones = serializers.SerializerMethodField()

    def get_custom_geo_zones(self, obj: Parcel):
        geo_custom_zones_data = GeoCustomZone.objects.order_by(
            *GEO_CUSTOM_ZONES_ORDER_BYS
        ).filter(geo_custom_zone_status=GeoCustomZoneStatus.ACTIVE)
        geo_custom_zones_data = geo_custom_zones_data.filter(
            geometry__intersects=obj.geometry
        )
        geo_custom_zones_data = geo_custom_zones_data.values(
            "uuid", "name", "color", "geo_custom_zone_status"
        )
        geo_custom_zones_data = geo_custom_zones_data.all()

        geo_custom_zones = []

        for geo_custom_zone in geo_custom_zones_data:
            geo_custom_zones.append(GeoCustomZoneSerializer(geo_custom_zone).data)

        return geo_custom_zones
