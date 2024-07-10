from rest_framework import serializers

from core.serializers.object_type import ObjectTypeSerializer
from core.serializers.tile_set import TileSetMinimalSerializer
from django.contrib.gis.db import models as models_gis


class MapSettingTileSetSerializer(serializers.Serializer):
    tile_set = TileSetMinimalSerializer()
    geometry = models_gis.GeometryField()


class MapSettingsSerializer(serializers.Serializer):
    tile_set_settings = MapSettingTileSetSerializer(many=True)
    object_types = ObjectTypeSerializer(many=True)
    global_geometry = models_gis.GeometryField(null=True)
