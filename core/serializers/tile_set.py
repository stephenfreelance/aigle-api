from core.models.tile_set import TileSet
from core.serializers import UuidTimestampedModelSerializerMixin


class TileSetMinimalSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = TileSet
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "name",
            "url",
            "tile_set_status",
            "tile_set_scheme",
            "tile_set_type",
            "date",
        ]


class TileSetSerializer(TileSetMinimalSerializer):
    class Meta(TileSetMinimalSerializer.Meta):
        model = TileSet
        fields = TileSetMinimalSerializer.Meta.fields + [
            "geometry",
        ]
