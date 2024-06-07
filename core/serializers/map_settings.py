from rest_framework import serializers

from core.serializers.tile_set import TileSetSerializer


class MapSettingsSerializer(serializers.Serializer):
    tile_sets = TileSetSerializer(many=True)
