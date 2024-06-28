from rest_framework import serializers

from core.serializers.object_type import ObjectTypeSerializer
from core.serializers.tile_set import TileSetMinimalSerializer


class MapSettingSerializer(serializers.Serializer):
    tile_set = TileSetMinimalSerializer()
    object_types = ObjectTypeSerializer(many=True)
    user_group_rights = serializers.ListField(child=serializers.CharField())


class MapSettingsSerializer(serializers.Serializer):
    settings = MapSettingSerializer(many=True)
