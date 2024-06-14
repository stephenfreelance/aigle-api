from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Case, When, Value

from core.models.object_type import ObjectType
from core.models.tile_set import TileSet, TileSetStatus, TileSetType
from core.serializers.map_settings import MapSettingsSerializer
from core.serializers.object_type import ObjectTypeSerializer
from core.serializers.tile_set import TileSetSerializer


class MapSettingsView(APIView):
    def get(self, request, format=None):
        tile_sets = (
            TileSet.objects.filter(tile_set_status=TileSetStatus.VISIBLE)
            .order_by(
                Case(
                    When(tile_set_type=TileSetType.INDICATIVE, then=Value(0)),
                    When(tile_set_type=TileSetType.PARTIAL, then=Value(1)),
                    When(tile_set_type=TileSetType.BACKGROUND, then=Value(2)),
                ),
                "-date",
            )
            .all()
        )
        serialized_tile_sets = TileSetSerializer(tile_sets, many=True).data

        object_types = ObjectType.objects.order_by("name").all()
        serialized_object_types = ObjectTypeSerializer(object_types, many=True).data

        settings = MapSettingsSerializer(
            data={
                "tile_sets": serialized_tile_sets,
                "object_types": serialized_object_types,
            }
        )

        settings.is_valid()
        return Response(settings.data)
