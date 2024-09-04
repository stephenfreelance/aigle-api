from common.constants.models import DEFAULT_MAX_LENGTH
from core.models.geo_zone import GeoZone
from django.db import models
from django.contrib.gis.db import models as models_gis


class GeoCustomZoneStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "ACTIVE"
    INACTIVE = "INACTIVE", "INACTIVE"


class GeoCustomZone(GeoZone):
    color = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    geo_custom_zone_status = models.CharField(
        max_length=DEFAULT_MAX_LENGTH,
        choices=GeoCustomZoneStatus.choices,
        default=GeoCustomZoneStatus.ACTIVE,
    )
    geometry_simplified = models_gis.GeometryField(null=True)
