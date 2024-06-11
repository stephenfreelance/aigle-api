from core.models.detection import Detection, DetectionSource
from core.models.detection_data import (
    DetectionControlStatus,
    DetectionData,
    DetectionValidationStatus,
)
from core.models.detection_object import DetectionObject
from core.models.object_type import ObjectType
from core.serializers import UuidTimestampedModelSerializerMixin
from core.serializers.detection_data import DetectionDataInputSerializer

from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers


class DetectionMinimalSerializer(
    UuidTimestampedModelSerializerMixin, GeoFeatureModelSerializer
):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = Detection
        geo_field = "geometry"
        fields = [
            "uuid",
            "object_type_uuid",
            "object_type_color",
            "detection_control_status",
            "detection_validation_status",
        ]

    object_type_uuid = serializers.CharField(source="detection_object.object_type.uuid")
    object_type_color = serializers.CharField(
        source="detection_object.object_type.color"
    )
    detection_control_status = serializers.ChoiceField(
        source="detection_data.detection_control_status",
        choices=DetectionControlStatus.choices,
    )
    detection_validation_status = serializers.ChoiceField(
        source="detection_data.detection_validation_status",
        choices=DetectionValidationStatus.choices,
    )


class DetectionSerializer(
    UuidTimestampedModelSerializerMixin, GeoFeatureModelSerializer
):
    from core.serializers.detection_data import DetectionDataSerializer

    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = Detection
        geo_field = "geometry"
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "geometry",
            "score",
            "detection_source",
            "detection_data",
        ]

    detection_data = DetectionDataSerializer(read_only=True)


class DetectionDetailSerializer(DetectionSerializer):
    from core.serializers.detection_object import DetectionObjectSerializer

    class Meta(DetectionSerializer.Meta):
        fields = DetectionSerializer.Meta.fields + [
            "detection_object",
        ]

    detection_object = DetectionObjectSerializer(read_only=True)


class DetectionInputSerializer(DetectionSerializer):
    from core.serializers.detection_object import DetectionObjectInputSerializer

    class Meta(DetectionSerializer.Meta):
        fields = [
            "geometry",
            "detection_data",
            "detection_object",
        ]

    detection_object = DetectionObjectInputSerializer()
    detection_data = DetectionDataInputSerializer()

    def create(self, validated_data):
        # create detection object

        detection_object_data = validated_data.pop("detection_object")

        object_type_uuid = detection_object_data.pop("object_type_uuid")
        object_type = ObjectType.objects.filter(uuid=object_type_uuid).first()
        if not object_type:
            raise serializers.ValidationError(
                f"Object type with following uuid not found: {object_type_uuid}"
            )

        detection_object = DetectionObject(**detection_object_data)
        detection_object.object_type = object_type
        detection_object.save()

        # create detection data

        detection_data = DetectionData(**validated_data.pop("detection_data"))
        detection_data.user_last_update_user = self.context["request"].user
        detection_data.save()

        # create detection

        instance = Detection(**validated_data)
        instance.detection_object = detection_object
        instance.detection_data = detection_data
        instance.score = 1
        instance.detection_source = DetectionSource.INTERFACE_DRAWN
        instance.save()

        return instance
