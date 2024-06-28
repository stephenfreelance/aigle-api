from core.models.detection import Detection, DetectionSource
from core.models.detection_data import (
    DetectionControlStatus,
    DetectionData,
    DetectionValidationStatus,
)
from core.models.detection_object import DetectionObject
from core.models.object_type import ObjectType
from core.models.tile import TILE_DEFAULT_ZOOM, Tile
from core.models.tile_set import TileSet
from core.serializers import UuidTimestampedModelSerializerMixin
from core.serializers.detection_data import DetectionDataInputSerializer

from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers

from core.serializers.tile import TileSerializer
from core.serializers.tile_set import TileSetMinimalSerializer
from django.contrib.gis.db.models.functions import Centroid


class DetectionMinimalSerializer(
    UuidTimestampedModelSerializerMixin, GeoFeatureModelSerializer
):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = Detection
        geo_field = "geometry"
        fields = [
            "id",
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


class DetectionSerializer(UuidTimestampedModelSerializerMixin):
    from core.serializers.detection_data import DetectionDataSerializer

    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = Detection
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "id",
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
            "tile",
            "tile_set",
        ]

    detection_object = DetectionObjectSerializer(read_only=True)
    tile = TileSerializer(read_only=True)
    tile_set = TileSetMinimalSerializer(read_only=True)


class DetectionInputSerializer(DetectionSerializer):
    from core.serializers.detection_object import DetectionObjectInputSerializer

    class Meta(DetectionSerializer.Meta):
        fields = ["geometry", "detection_data", "detection_object", "tile_set_uuid"]

    detection_object = DetectionObjectInputSerializer()
    detection_data = DetectionDataInputSerializer(required=False)
    tile_set_uuid = serializers.UUIDField(write_only=True)

    def create(self, validated_data):
        # create detection object

        detection_object_data = validated_data.pop("detection_object")

        object_type_uuid = detection_object_data.pop("object_type_uuid")
        object_type = ObjectType.objects.filter(uuid=object_type_uuid).first()

        if not object_type:
            raise serializers.ValidationError(
                f"Object type with following uuid not found: {
                    object_type_uuid}"
            )

        # get tile_set and tile

        tile = Tile.objects.filter(
            geometry__contains=Centroid(validated_data["geometry"]), z=TILE_DEFAULT_ZOOM
        ).first()

        if not tile:
            raise serializers.ValidationError("Tile not found for specified geometry")

        tile_set_uuid = validated_data.pop("tile_set_uuid")
        tile_set = TileSet.objects.filter(
            uuid=tile_set_uuid,
        ).first()

        if not object_type:
            raise serializers.ValidationError(
                f"Tile set with following uuid not found: {tile_set_uuid}"
            )

        detection_object = DetectionObject(**detection_object_data)
        detection_object.object_type = object_type
        detection_object.save()

        # create detection data

        detection_data_data = validated_data.pop("detection_data", None)

        if detection_data_data:
            detection_data = DetectionData(**detection_data_data)
        else:
            # default value
            detection_data = DetectionData(
                detection_control_status=DetectionControlStatus.NO_CONTROL,
                detection_validation_status=DetectionValidationStatus.SUSPECT,
            )

        detection_data.user_last_update = self.context["request"].user
        detection_data.save()

        # create detection

        instance = Detection(**validated_data)

        instance.detection_object = detection_object
        instance.detection_data = detection_data
        instance.tile_set = tile_set
        instance.tile = tile

        instance.score = 1
        instance.detection_source = DetectionSource.INTERFACE_DRAWN
        instance.save()

        return instance


class DetectionUpdateSerializer(DetectionSerializer):
    class Meta(DetectionSerializer.Meta):
        fields = ["object_type_uuid"]

    object_type_uuid = serializers.UUIDField(write_only=True)

    def update(self, instance: Detection, validated_data):
        object_type_uuid = validated_data.get("object_type_uuid")

        if object_type_uuid:
            object_type = ObjectType.objects.filter(uuid=object_type_uuid).first()

            if not object_type:
                raise serializers.ValidationError(
                    f"Object type with following uuid not found: {
                        object_type_uuid}"
                )

            instance.detection_object.object_type = object_type
            instance.detection_object.save()

        instance.save()

        return instance
