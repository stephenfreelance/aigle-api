from django.utils import timezone
from typing import List, Optional
from core.models.detection_object import DetectionObject
from core.models.object_type import ObjectType
from core.models.tile_set import TileSet, TileSetType
from core.serializers import UuidTimestampedModelSerializerMixin

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


class DetectionObjectDetailSerializer(DetectionObjectSerializer):
    from core.serializers.detection import DetectionWithTileSerializer

    class Meta(DetectionObjectSerializer.Meta):
        fields = DetectionObjectSerializer.Meta.fields + [
            "id",
            "detections",
            "tile_sets_previews",
        ]

    detections = DetectionWithTileSerializer(many=True)
    tile_sets_previews = serializers.SerializerMethodField()

    def get_tile_sets_previews(self, obj):
        user = self.context["request"].user
        tile_sets = get_user_tile_sets(
            user=user,
            filter_tile_set_type__in=[TileSetType.PARTIAL, TileSetType.BACKGROUND],
            order_bys=["-date"],
        )

        if not tile_sets:
            return []

        # get at least 6 years old
        tile_set_six_years = (
            get_tile_set_years_ago(tile_sets=tile_sets, relative_years=6)
            or tile_sets[len(tile_sets) - 1]
        )
        tile_set_three_years = (
            get_tile_set_years_ago(tile_sets=tile_sets, relative_years=3)
            or tile_sets[len(tile_sets) - 1]
        )
        tile_set_most_recent = tile_sets[0]

        tile_sets_serialized = TileSetMinimalSerializer(
            data=[
                tile_set_six_years,
                tile_set_three_years,
                tile_set_most_recent,
            ],
            many=True,
        )
        tile_sets_serialized.is_valid()
        return tile_sets_serialized.data


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
