import json
from rest_framework.views import APIView
from rest_framework.response import Response

from core.contants.order_by import TILE_SETS_ORDER_BYS
from core.models.object_type import ObjectType
from core.models.tile_set import TileSet, TileSetStatus
from core.models.user import UserRole
from core.models.user_group import UserGroupRight
from core.serializers.map_settings import (
    MapSettingsSerializer,
    MapSettingTileSetSerializer,
)
from core.serializers.object_type import ObjectTypeSerializer
from core.serializers.tile_set import TileSetMinimalSerializer
from django.contrib.gis.geos import GEOSGeometry

from django.contrib.gis.db.models.aggregates import Union

from core.utils.data_permissions import get_user_tile_sets


class MapSettingsView(APIView):
    def get(self, request, format=None):
        setting_tile_sets = []
        object_types = []

        # super admin has access to all tile sets and all object types
        if request.user.user_role == UserRole.SUPER_ADMIN:
            tile_sets = TileSet.objects.filter(
                tile_set_status__in=[TileSetStatus.VISIBLE, TileSetStatus.HIDDEN]
            ).order_by(*TILE_SETS_ORDER_BYS)

            tile_sets = tile_sets.annotate(
                intersection=Union("geo_zones__geometry")
            ).all()

            object_types_objects = ObjectType.objects.all()
            object_types_serialized = ObjectTypeSerializer(
                data=object_types_objects, many=True
            )
            object_types_serialized.is_valid()
            object_types = object_types_serialized.data

            for tile_set in tile_sets:
                setting_tile_set = MapSettingTileSetSerializer(
                    data={
                        "tile_set": TileSetMinimalSerializer(tile_set).data,
                        "geometry": (
                            json.loads(GEOSGeometry(tile_set.intersection).geojson)
                            if tile_set.intersection
                            else None
                        ),
                    }
                )
                setting_tile_sets.append(setting_tile_set.initial_data)

        if request.user.user_role != UserRole.SUPER_ADMIN:
            tile_sets = get_user_tile_sets(request.user)

            for tile_set in tile_sets:
                setting_tile_set = MapSettingTileSetSerializer(
                    data={
                        "tile_set": TileSetMinimalSerializer(tile_set).data,
                        "geometry": (
                            json.loads(GEOSGeometry(tile_set.intersection).geojson)
                            if tile_set.intersection
                            else None
                        ),
                    }
                )

                setting_tile_sets.append(setting_tile_set.initial_data)
                object_types_objects = (
                    ObjectType.objects.filter(
                        categories__user_groups__user_user_groups__user__id=request.user.id
                    )
                    .distinct()
                    .all()
                )
                object_types_serialized = ObjectTypeSerializer(
                    data=object_types_objects, many=True
                )
                object_types_serialized.is_valid()
                object_types = object_types_serialized.data

        setting = MapSettingsSerializer(
            data={
                "tile_set_settings": setting_tile_sets,
                "object_types": object_types,
            }
        )

        setting.is_valid()

        return Response(setting.data)
