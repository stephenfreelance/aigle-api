from django.utils import timezone
from typing import List, Optional
from core.models.detection_object import DetectionObject
from core.models.object_type import ObjectType
from core.models.tile_set import TileSet, TileSetType
from core.models.user import UserRole
from core.models.user_group import UserGroupRight
from core.serializers import UuidTimestampedModelSerializerMixin
from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.db.models.functions import Centroid

from core.serializers.detection import (
    DetectionWithTileMinimalSerializer,
    DetectionWithTileSerializer,
)
from core.serializers.object_type import ObjectTypeSerializer
from rest_framework import serializers

from core.serializers.tile_set import TileSetMinimalSerializer
from core.utils.data_permissions import get_user_tile_sets


class DetectionObjectSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = DetectionObject
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "id",
            "address",
            "object_type",
        ]

    object_type = ObjectTypeSerializer(read_only=True)


class DetectionHistorySerializer(serializers.Serializer):
    tile_set = TileSetMinimalSerializer(read_only=True)
    detection = DetectionWithTileMinimalSerializer(read_only=True, required=False)


class DetectionObjectHistorySerializer(DetectionObjectSerializer):
    class Meta(DetectionObjectSerializer.Meta):
        fields = DetectionObjectSerializer.Meta.fields + [
            "id",
            "detections",
        ]

    detections = serializers.SerializerMethodField()

    def get_detections(self, obj: DetectionObject):
        user = self.context["request"].user
        detections = obj.detections.all()
        tile_sets = get_user_tile_sets(
            user=user,
            filter_tile_set_type__in=[TileSetType.PARTIAL, TileSetType.BACKGROUND],
            order_bys=["-date"],
            filter_tile_set_contains_point=Centroid(detections[0].geometry),
        )

        if not tile_sets:
            return []

        detection_history = []
        tile_set_id_detection_map = {
            detection.tile_set.id: detection for detection in detections
        }

        for tile_set in list(sorted(tile_sets, key=lambda t: t.date)):
            detection = tile_set_id_detection_map.get(tile_set.id, None)

            history = DetectionHistorySerializer(
                data={
                    "tile_set": TileSetMinimalSerializer(tile_set).data,
                    "detection": DetectionWithTileMinimalSerializer(detection).data
                    if detection
                    else None,
                }
            )
            detection_history.append(history.initial_data)

        return detection_history


class DetectionObjectTileSetPreview(serializers.Serializer):
    preview = serializers.BooleanField()
    tile_set = TileSetMinimalSerializer()


class DetectionObjectDetailSerializer(DetectionObjectSerializer):
    class Meta(DetectionObjectSerializer.Meta):
        fields = DetectionObjectSerializer.Meta.fields + [
            "id",
            "detections",
            "tile_sets",
            "user_group_rights",
        ]

    detections = DetectionWithTileSerializer(many=True)
    tile_sets = serializers.SerializerMethodField()
    user_group_rights = serializers.SerializerMethodField()

    def get_tile_sets(self, obj: DetectionObject):
        user = self.context["request"].user
        tile_sets = get_user_tile_sets(
            user=user,
            filter_tile_set_type__in=[TileSetType.PARTIAL, TileSetType.BACKGROUND],
            order_bys=["-date"],
            filter_tile_set_contains_point=Centroid(obj.detections.all()[0].geometry),
        )

        if not tile_sets:
            return []

        tile_sets_map = {}
        tile_set_six_years = (
            get_tile_set_years_ago(tile_sets=tile_sets, relative_years=6)
            or tile_sets[len(tile_sets) - 1]
        )
        tile_sets_map[tile_set_six_years.id] = tile_set_six_years

        # append most recent
        tile_sets_map[tile_sets[0].id] = tile_sets[0]

        for tile_set in tile_sets:
            if not tile_sets_map.get(tile_set.id):
                tile_sets_map[tile_set.id] = tile_set
                break

        tile_set_previews = []

        for tile_set in sorted(tile_sets, key=lambda t: t.date):
            preview = DetectionObjectTileSetPreview(
                data={
                    "tile_set": TileSetMinimalSerializer(tile_set).data,
                    "preview": True if tile_sets_map.get(tile_set.id) else False,
                }
            )
            tile_set_previews.append(preview.initial_data)

        return tile_set_previews

    def get_user_group_rights(self, obj: DetectionObject):
        user = self.context["request"].user

        if user.user_role == UserRole.SUPER_ADMIN:
            return [
                UserGroupRight.WRITE,
                UserGroupRight.ANNOTATE,
                UserGroupRight.READ,
            ]

        user_user_groups = user.user_user_groups.annotate(
            union_geometry=Union("user_group__geo_zones__geometry")
        )
        user_user_groups = user_user_groups.filter(
            union_geometry__contains=Centroid(obj.detections.first().geometry)
        )

        user_group_rights = set()

        for user_user_group in user_user_groups:
            user_group_rights.update(user_user_group.user_group_rights)

        return list(user_group_rights)


class DetectionObjectInputSerializer(DetectionObjectSerializer):
    class Meta(DetectionObjectSerializer.Meta):
        fields = ["address", "object_type_uuid"]

    object_type_uuid = serializers.UUIDField(write_only=True)

    def update(self, instance, validated_data):
        object_type_uuid = validated_data.pop("object_type_uuid")
        object_type = ObjectType.objects.filter(uuid=object_type_uuid).first()

        if not object_type:
            raise serializers.ValidationError(
                f"Object type with following uuid not found: {
                    object_type_uuid}"
            )

        instance.object_type = object_type
        instance.save()

        return instance


# utils


def get_tile_set_years_ago(
    tile_sets: List[TileSet], relative_years: int
) -> Optional[TileSet]:
    tile_set_years_ago = None
    date_years_ago = timezone.now()
    date_years_ago = date_years_ago.replace(year=date_years_ago.year - relative_years)

    for tile_set in tile_sets:
        if tile_set.date <= date_years_ago:
            tile_set_years_ago = tile_set
            break

    return tile_set_years_ago
