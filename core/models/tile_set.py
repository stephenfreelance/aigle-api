from django.db import models


from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin

from core.models.geo_commune import GeoCommune
from core.models.geo_department import GeoDepartment
from core.models.geo_region import GeoRegion


from django.contrib.gis.db.models.aggregates import Union
from django.db.models import Value
from django.db.models.functions import Coalesce


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

    communes = models.ManyToManyField(GeoCommune, related_name="tile_sets")
    departments = models.ManyToManyField(GeoDepartment, related_name="tile_sets")
    regions = models.ManyToManyField(GeoRegion, related_name="tile_sets")

    @property
    def geometry(self):
        communes_union = self.communes.aggregate(
            combined=Coalesce(Union("geometry"), Value(None))
        )["combined"]
        departments_union = self.departments.aggregate(
            combined=Coalesce(Union("geometry"), Value(None))
        )["combined"]
        regions_union = self.regions.aggregate(
            combined=Coalesce(Union("geometry"), Value(None))
        )["combined"]

        all_unions = [
            geom
            for geom in [communes_union, departments_union, regions_union]
            if geom is not None
        ]
        if all_unions:
            final_union = all_unions[0]
            for geom in all_unions[1:]:
                final_union = final_union.union(geom)
            return final_union

        return None
