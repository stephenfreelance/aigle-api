from django.db import models


from common.constants.models import DEFAULT_MAX_LENGTH
from core.models.geo_region import GeoRegion
from django.core.validators import MinValueValidator

from core.models.geo_zone import GeoZone


class GeoDepartment(GeoZone):
    insee_code = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    surface_km2 = models.IntegerField(validators=[MinValueValidator(0)])
    region = models.ForeignKey(
        GeoRegion, related_name="departments", on_delete=models.CASCADE
    )
