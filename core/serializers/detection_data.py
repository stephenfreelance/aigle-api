from core.models.detection_data import DetectionData
from core.serializers import UuidTimestampedModelSerializerMixin


class DetectionDataSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = DetectionData
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "detection_control_status",
            "detection_validation_status",
            "user_last_update_user",
        ]


class DetectionDataInputSerializer(DetectionDataSerializer):
    class Meta(DetectionDataSerializer.Meta):
        fields = [
            "detection_control_status",
            "detection_validation_status",
        ]
