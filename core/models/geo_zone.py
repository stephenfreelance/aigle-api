from django.db import models

from django.contrib.gis.db import models as models_gis


from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin


class GeoZoneType(models.TextChoices):
    COMMUNE = "COMMUNE", "COMMUNE"
    DEPARTMENT = "DEPARTMENT", "DEPARTMENT"
    REGION = "REGION", "REGION"
    CUSTOM = "CUSTOM", "CUSTOM"


class GeoZone(TimestampedModelMixin, UuidModelMixin, DeletableModelMixin):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    geometry = models_gis.GeometryField()
    geo_zone_type = models.CharField(
        max_length=DEFAULT_MAX_LENGTH,
        choices=GeoZoneType.choices,
        editable=False,
    )

    def save(self, *args, **kwargs):
        self.type = self.__class__.__name__
        import pdb

        pdb.set_trace()
        super().save(*args, **kwargs)
