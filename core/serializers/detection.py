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
            "uuid",
            "object_type_uuid",
            "object_type_color",
            "detection_control_status",
            "detection_validation_status",
            "detection_object_uuid",
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
    detection_object_uuid = serializers.CharField(source="detection_object.uuid")


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


class DetectionWithTileMinimalSerializer(DetectionSerializer):
    class Meta(DetectionSerializer.Meta):
        fields = DetectionSerializer.Meta.fields + [
            "tile",
        ]

    tile = TileSerializer(read_only=True)

class DetectionWithTileSerializer(DetectionWithTileMinimalSerializer):
    class Meta(DetectionWithTileMinimalSerializer.Meta):
        fields = DetectionWithTileMinimalSerializer.Meta.fields + [
            "tile_set",
        ]

    tile_set = TileSetMinimalSerializer(read_only=True)


class DetectionDetailSerializer(DetectionWithTileSerializer):
    from core.serializers.detection_object import DetectionObjectSerializer

    class Meta(DetectionWithTileSerializer.Meta):
        fields = DetectionWithTileSerializer.Meta.fields + [
            "detection_object",
        ]

    detection_object = DetectionObjectSerializer(read_only=True)


class DetectionInputSerializer(DetectionSerializer):
    from core.serializers.detection_object import DetectionObjectInputSerializer

    class Meta(DetectionSerializer.Meta):
        fields = ["geometry", "detection_data", "detection_object", "detection_object_uuid", "tile_set_uuid"]

    detection_object = DetectionObjectInputSerializer(required=False)
    detection_data = DetectionDataInputSerializer(required=False)
    tile_set_uuid = serializers.UUIDField(write_only=True)
    detection_object_uuid = serializers.UUIDField(write_only=True, required=False)

    def create(self, validated_data):
        # create or retrieve detection object

        detection_object_uuid = validated_data.pop("detection_object_uuid", None)
        
        tile_set_uuid = validated_data.pop("tile_set_uuid")
        tile_set = None

        if tile_set_uuid:
            tile_set = TileSet.objects.filter(
                uuid=tile_set_uuid,
            ).first()

            if not tile_set:
                raise serializers.ValidationError(
                    f"Tile set with following uuid not found: {tile_set_uuid}"
                )
    
        tile = Tile.objects.filter(
            geometry__contains=Centroid(validated_data["geometry"]), z=TILE_DEFAULT_ZOOM
        ).first()

        if not tile:
            raise serializers.ValidationError("Tile not found for specified geometry")
            

        if not detection_object_uuid:
            detection_object_data = validated_data.pop("detection_object", None)

            if not detection_object_data:
                raise serializers.ValidationError("detectionObjectUuid or detectionObject must be specified")

            object_type_uuid = detection_object_data.pop("object_type_uuid")
            object_type = ObjectType.objects.filter(uuid=object_type_uuid).first()

            if not object_type:
                raise serializers.ValidationError(
                    f"Object type with following uuid not found: {
                        object_type_uuid}"
                )

            # get tile_set and tile

            detection_object = DetectionObject(**detection_object_data)
            detection_object.object_type = object_type
            detection_object.save()
        
        if detection_object_uuid:
            detection_object = DetectionObject.objects.filter(uuid=detection_object_uuid).first()

            if not detection_object:
                raise serializers.ValidationError(
                    f"Detection object with following uuid not found: {detection_object_uuid}"
                )


        # create detection data

        detection_data_data = validated_data.pop("detection_data", None)

        if detection_data_data:
            detection_data = DetectionData(**detection_data_data)
        else:
            # default value
            detection_data = DetectionData(
                detection_control_status=DetectionControlStatus.DETECTED,
                detection_validation_status=DetectionValidationStatus.SUSPECT,
            )

        detection_data.user_last_update = self.context["request"].user
        detection_data.save()

        # create detection

        instance = Detection(**validated_data)

        instance.detection_object = detection_object
        instance.detection_data = detection_data
        
        if tile_set:
            instance.tile_set = tile_set
        
        if tile:
            instance.tile = tile
        
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
