from core.models.detection_data import DetectionData
from core.serializers import UuidTimestampedModelSerializerMixin

from rest_framework import serializers


class DetectionDataSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = DetectionData
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "detection_control_status",
            "detection_validation_status",
            "user_last_update_uuid",
        ]

    user_last_update_uuid = serializers.UUIDField(
        source="user_last_update.uuid", read_only=True
    )


class DetectionDataInputSerializer(DetectionDataSerializer):
    class Meta(DetectionDataSerializer.Meta):
        fields = [
            "detection_control_status",
            "detection_validation_status",
        ]
