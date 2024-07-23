from core.models.detection_object import DetectionObject
from core.models.parcel import Parcel
from core.serializers import UuidTimestampedModelSerializerMixin
from core.serializers.detection import DetectionWithTileSerializer
from core.serializers.geo_commune import GeoCommuneSerializer
from core.serializers.detection_object import DetectionObjectMinimalSerializer

from rest_framework import serializers


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
        fields = ParcelSerializer.Meta.fields + ["detection_objects"]

    detection_objects = ParcelDetectionObjectSerializer(many=True)
