from django.utils import timezone
from typing import List, Optional
from core.contants.order_by import GEO_CUSTOM_ZONES_ORDER_BYS
from core.models.detection_object import DetectionObject
from core.models.geo_custom_zone import GeoCustomZone, GeoCustomZoneStatus
from core.models.object_type import ObjectType
from core.models.tile_set import TileSet, TileSetType
from core.models.user_group import UserGroupRight
from core.serializers import UuidTimestampedModelSerializerMixin
from django.contrib.gis.db.models.functions import Centroid

from core.serializers.detection import (
    DetectionWithTileMinimalSerializer,
    DetectionWithTileSerializer,
)
from core.serializers.geo_custom_zone import GeoCustomZoneSerializer
from core.serializers.object_type import ObjectTypeSerializer
from rest_framework import serializers

from core.serializers.tile_set import TileSetMinimalSerializer
from core.utils.data_permissions import get_user_group_rights, get_user_tile_sets
from core.utils.prescription import compute_prescription


class DetectionObjectMinimalSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = DetectionObject
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "id",
            "address",
            "object_type",
        ]

    object_type = ObjectTypeSerializer(read_only=True)


class DetectionObjectSerializer(DetectionObjectMinimalSerializer):
    from core.serializers.parcel import ParcelMinimalSerializer

    class Meta(DetectionObjectMinimalSerializer.Meta):
        fields = DetectionObjectMinimalSerializer.Meta.fields + [
            "parcel",
        ]

    parcel = ParcelMinimalSerializer(read_only=True)


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
        tile_sets, global_geometry = get_user_tile_sets(
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
    from core.serializers.parcel import ParcelSerializer

    class Meta(DetectionObjectSerializer.Meta):
        fields = DetectionObjectSerializer.Meta.fields + [
            "id",
            "detections",
            "tile_sets",
            "user_group_rights",
            "custom_geo_zones"
        ]

    detections = serializers.SerializerMethodField()
    tile_sets = serializers.SerializerMethodField()
    user_group_rights = serializers.SerializerMethodField()
    parcel = ParcelSerializer(read_only=True)
    custom_geo_zones = serializers.SerializerMethodField()

    def get_detections(self, obj: DetectionObject):
        user = self.context["request"].user

        if self.context.get("tile_sets"):
            tile_sets = self.context["tile_sets"]
        else:
            tile_sets, global_geometry = get_user_tile_sets(
                user=user,
                filter_tile_set_type__in=[TileSetType.PARTIAL, TileSetType.BACKGROUND],
                order_bys=["-date"],
                filter_tile_set_contains_point=Centroid(
                    obj.detections.all()[0].geometry
                ),
            )
            self.context["tile_sets"] = tile_sets

        detections = obj.detections.filter(tile_set__in=tile_sets)

        detections_serialized = DetectionWithTileSerializer(data=detections, many=True)
        detections_serialized.is_valid()

        return detections_serialized.data

    def get_tile_sets(self, obj: DetectionObject):
        user = self.context["request"].user

        if self.context.get("tile_sets"):
            tile_sets = self.context["tile_sets"]
        else:
            tile_sets, global_geometry = get_user_tile_sets(
                user=user,
                filter_tile_set_type__in=[TileSetType.PARTIAL, TileSetType.BACKGROUND],
                order_bys=["-date"],
                filter_tile_set_contains_point=Centroid(
                    obj.detections.all()[0].geometry
                ),
            )
            self.context["tile_sets"] = tile_sets

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
        point = Centroid(obj.detections.first().geometry)

        return get_user_group_rights(user=user, point=point)


    def get_custom_geo_zones(self, obj: DetectionObject):
        geo_custom_zones_data = GeoCustomZone.objects.order_by(
            *GEO_CUSTOM_ZONES_ORDER_BYS
        ).filter(geo_custom_zone_status=GeoCustomZoneStatus.ACTIVE)
        geo_custom_zones_data = geo_custom_zones_data.filter(
            geometry__intersects=obj.detections.all()[0].geometry
        )
        geo_custom_zones_data = geo_custom_zones_data.values(
            "uuid", "name", "color", "geo_custom_zone_status"
        )
        geo_custom_zones_data = geo_custom_zones_data.all()

        geo_custom_zones = []

        for geo_custom_zone in geo_custom_zones_data:
            geo_custom_zones.append(GeoCustomZoneSerializer(geo_custom_zone).data)

        return geo_custom_zones

class DetectionObjectInputSerializer(DetectionObjectSerializer):
    class Meta(DetectionObjectSerializer.Meta):
        fields = ["address", "object_type_uuid"]

    object_type_uuid = serializers.UUIDField(write_only=True)

    def update(self, instance, validated_data):
        object_type = None
        object_type_uuid = validated_data.pop("object_type_uuid", None)

        if object_type_uuid:
            object_type = ObjectType.objects.filter(uuid=object_type_uuid).first()

            if not object_type:
                raise serializers.ValidationError(
                    f"Object type with following uuid not found: {
                        object_type_uuid}"
                )

        user = self.context["request"].user
        centroid = Centroid(instance.detections.first().geometry)

        get_user_group_rights(
            user=user, point=centroid, raise_if_has_no_right=UserGroupRight.WRITE
        )

        if object_type:
            instance.object_type = object_type
            compute_prescription(instance)

        for key, value in validated_data.items():
            setattr(instance, key, value)

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
