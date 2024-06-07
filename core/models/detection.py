from django.db import models


from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin
from core.models.detected_object import DetectedObject
from core.models.detection_data import DetectionData
from django.contrib.gis.db import models as models_gis
from django.core.validators import MinValueValidator


class DetectionSource(models.TextChoices):
    INTERFACE_DRAWN = "INTERFACE_DRAWN", "INTERFACE_DRAWN"
    ANALYSIS = "ANALYSIS", "ANALYSIS"


class Detection(TimestampedModelMixin, UuidModelMixin, DeletableModelMixin):
    geometry = models_gis.GeometryField()
    score = models.FloatField(validators=[MinValueValidator(0)])
    detection_source = models.CharField(
        max_length=DEFAULT_MAX_LENGTH,
        choices=DetectionSource.choices,
    )
    detected_object = models.ForeignKey(
        DetectedObject, related_name="detections", on_delete=models.CASCADE
    )
    detection_data = models.OneToOneField(
        DetectionData, related_name="detection", on_delete=models.CASCADE
    )
