from rest_framework import serializers

from core.serializers.object_type import ObjectTypeSerializer
from core.serializers.tile_set import TileSetSerializer


class MapSettingsSerializer(serializers.Serializer):
    tile_sets = TileSetSerializer(many=True)
    object_types = ObjectTypeSerializer(many=True)
