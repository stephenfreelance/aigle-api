from core.models.detection_object import DetectionObject
from core.serializers import UuidTimestampedModelSerializerMixin
from core.serializers.detection import DetectionSerializer

from core.serializers.object_type import ObjectTypeSerializer
from rest_framework import serializers


class DetectionObjectSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = DetectionObject
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "address",
            "object_type",
        ]

    object_type = ObjectTypeSerializer(read_only=True)


class DetectionObjectDetailSerializer(DetectionObjectSerializer):
    class Meta(DetectionObjectSerializer.Meta):
        fields = DetectionObjectSerializer.Meta.fields + [
            "detections",
        ]

    detections = DetectionSerializer(many=True)


class DetectionObjectInputSerializer(DetectionObjectSerializer):
    class Meta(DetectionObjectSerializer.Meta):
        fields = ["address", "object_type_uuid"]

    object_type_uuid = serializers.UUIDField(write_only=True)
