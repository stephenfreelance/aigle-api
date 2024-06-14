from django.db import models


from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin


class TileSetStatus(models.TextChoices):
    VISIBLE = "VISIBLE", "VISIBLE"
    HIDDEN = "HIDDEN", "HIDDEN"
    DEACTIVATED = "DEACTIVATED", "DEACTIVATED"


class TileSetScheme(models.TextChoices):
    tms = "tms", "tms"
    xyz = "xyz", "xyz"


class TileSetType(models.TextChoices):
    BACKGROUND = "BACKGROUND", "BACKGROUND"
    PARTIAL = "PARTIAL", "PARTIAL"
    INDICATIVE = "INDICATIVE", "INDICATIVE"


class TileSet(TimestampedModelMixin, UuidModelMixin, DeletableModelMixin):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    url = models.URLField(max_length=1024, unique=True)
    tile_set_status = models.CharField(
        max_length=DEFAULT_MAX_LENGTH,
        choices=TileSetStatus.choices,
    )
    date = models.DateTimeField(unique=True)
    tile_set_scheme = models.CharField(
        max_length=DEFAULT_MAX_LENGTH, choices=TileSetScheme.choices
    )
    tile_set_type = models.CharField(
        max_length=DEFAULT_MAX_LENGTH,
        choices=TileSetType.choices,
    )
