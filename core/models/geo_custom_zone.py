from common.constants.models import DEFAULT_MAX_LENGTH
from core.models.geo_zone import GeoZone
from django.db import models


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
