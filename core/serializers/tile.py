from core.models.tile import Tile
from rest_framework import serializers


class TileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tile
        fields = ["x", "y", "z", "geometry"]
