from django.db.models import Case, When, Value

from core.models.tile_set import TileSetType

LAYERS_ORDER_BYS = [
    Case(
        When(tile_set_type=TileSetType.INDICATIVE, then=Value(0)),
        When(tile_set_type=TileSetType.PARTIAL, then=Value(1)),
        When(tile_set_type=TileSetType.BACKGROUND, then=Value(2)),
    ),
    "-date",
]
