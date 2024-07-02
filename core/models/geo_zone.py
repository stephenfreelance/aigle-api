from django.db import models

from django.contrib.gis.db import models as models_gis


from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin
from core.utils.string import normalize


class GeoZoneType(models.TextChoices):
    COMMUNE = "COMMUNE", "COMMUNE"
    DEPARTMENT = "DEPARTMENT", "DEPARTMENT"
    REGION = "REGION", "REGION"
    CUSTOM = "CUSTOM", "CUSTOM"


GEO_CLASS_NAMES_GEO_ZONE_TYPES_MAP = {
    "GeoCommune": GeoZoneType.COMMUNE,
    "GeoDepartment": GeoZoneType.DEPARTMENT,
    "GeoRegion": GeoZoneType.REGION,
    "GeoCustomZone": GeoZoneType.CUSTOM,
}


class GeoZone(TimestampedModelMixin, UuidModelMixin, DeletableModelMixin):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    name_normalized = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    geometry = models_gis.GeometryField()
    geo_zone_type = models.CharField(
        max_length=DEFAULT_MAX_LENGTH,
        choices=GeoZoneType.choices,
        editable=False,
    )

    def save(self, *args, **kwargs):
        self.geo_zone_type = GEO_CLASS_NAMES_GEO_ZONE_TYPES_MAP.get(
            self.__class__.__name__
        )

        if not self.geo_zone_type:
            raise ValueError(f"Unknown type for class: {self.__class__.__name__}")

        self.name_normalized = normalize(self.name)

        super().save(*args, **kwargs)
