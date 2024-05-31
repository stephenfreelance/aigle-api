from django.db import models

from django.contrib.gis.db import models as models_gis

from django.utils.translation import gettext_lazy as _

from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin
from django.core.validators import MinValueValidator


class GeoRegion(TimestampedModelMixin, UuidModelMixin, DeletableModelMixin):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    display_name = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    insee_code = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    surface_km2 = models.IntegerField(validators=[
        MinValueValidator(0)
    ])
    geometry = models_gis.GeometryField()
