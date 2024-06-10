from core.models.detection import Detection, DetectionSource
from core.models.detection_data import DetectionData
from core.models.detection_object import DetectionObject
from core.models.object_type import ObjectType
from core.serializers import UuidTimestampedModelSerializerMixin
from core.serializers.detection_data import DetectionDataInputSerializer

from rest_framework import serializers


class DetectionSerializer(UuidTimestampedModelSerializerMixin):
    from core.serializers.detection_data import DetectionDataSerializer

    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = Detection
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
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
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
