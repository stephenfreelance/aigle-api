from django.db import models

from django.contrib.gis.db import models as models_gis

from django.utils.translation import gettext_lazy as _

from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin
from django.core.validators import MinValueValidator


class ObjectType(TimestampedModelMixin, UuidModelMixin, DeletableModelMixin):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    color = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
