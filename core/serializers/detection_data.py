from core.models.detection_data import DetectionData
from core.models.user_group import UserGroupRight
from core.serializers import UuidTimestampedModelSerializerMixin
from django.contrib.gis.db.models.functions import Centroid

from rest_framework import serializers

from core.utils.data_permissions import get_user_group_rights


class DetectionDataSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = DetectionData
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "detection_control_status",
            "detection_validation_status",
            "detection_prescription_status",
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
            "detection_prescription_status",
        ]

    def update(self, instance, validated_data):
        user = self.context["request"].user
        centroid = Centroid(instance.detection.geometry)

        get_user_group_rights(
            user=user, point=centroid, raise_if_has_no_right=UserGroupRight.WRITE
        )

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.user_last_update = user
        instance.save()

        return instance
