from rest_framework.views import APIView
from rest_framework.response import Response

from core.models.tile_set import TileSet, TileSetStatus
from core.serializers.map_settings import MapSettingsSerializer
from core.serializers.tile_set import TileSetSerializer


class MapSettingsView(APIView):
    def get(self, request, format=None):
        tile_sets = (
            TileSet.objects.filter(tile_set_status=TileSetStatus.VISIBLE)
            .order_by("-date")
            .all()
        )

        serialized_tile_sets = TileSetSerializer(tile_sets, many=True).data
        settings = MapSettingsSerializer(data={"tile_sets": serialized_tile_sets})

        settings.is_valid()
        return Response(settings.data)
