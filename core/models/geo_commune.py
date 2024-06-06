from django.db import models

from django.contrib.gis.db import models as models_gis


from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin
from core.models.geo_department import GeoDepartment


class GeoCommune(TimestampedModelMixin, UuidModelMixin, DeletableModelMixin):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    display_name = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    iso_code = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    geometry = models_gis.GeometryField()
    department = models.ForeignKey(
        GeoDepartment, related_name="communes", on_delete=models.CASCADE
    )
