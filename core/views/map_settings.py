import json
from rest_framework.views import APIView
from rest_framework.response import Response

from core.contants.order_by import TILE_SETS_ORDER_BYS
from core.models.tile_set import TileSet, TileSetStatus
from core.models.user import UserRole
from core.serializers.map_settings import (
    MapSettingObjectTypeSerializer,
    MapSettingsSerializer,
    MapSettingTileSetSerializer,
)
from core.serializers.object_type import ObjectTypeSerializer
from core.serializers.tile_set import TileSetMinimalSerializer
from django.contrib.gis.geos import GEOSGeometry

from django.contrib.gis.db.models.aggregates import Union

from core.utils.data_permissions import (
    get_user_object_types_with_status,
    get_user_tile_sets,
)


class MapSettingsView(APIView):
    def get(self, request, format=None):
        setting_tile_sets = []
        global_geometry = None

        # super admin has access to all tile sets and all object types
        if request.user.user_role == UserRole.SUPER_ADMIN:
            tile_sets = TileSet.objects.filter(
                tile_set_status__in=[TileSetStatus.VISIBLE, TileSetStatus.HIDDEN]
            ).order_by(*TILE_SETS_ORDER_BYS)

            tile_sets = tile_sets.annotate(
                intersection=Union("geo_zones__geometry")
            ).all()

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
            tile_sets, global_geometry = get_user_tile_sets(request.user)

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

        object_types_with_status = get_user_object_types_with_status(request.user)
        setting_object_types = []

        for object_type, status in object_types_with_status:
            setting_object_type = MapSettingObjectTypeSerializer(
                data={
                    "object_type": ObjectTypeSerializer(object_type).data,
                    "object_type_category_object_type_status": status,
                }
            )
            setting_object_types.append(setting_object_type.initial_data)

        setting = MapSettingsSerializer(
            data={
                "tile_set_settings": setting_tile_sets,
                "object_type_settings": setting_object_types,
                "global_geometry": json.loads(GEOSGeometry(global_geometry).geojson)
                if global_geometry
                else None,
            }
        )

        return Response(setting.initial_data)
