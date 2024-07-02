from django.db import models


from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin

from core.models.user import User


class DetectionControlStatus(models.TextChoices):
    DETECTED = "DETECTED", "DETECTED"
    SIGNALED_INTERNALLY = "SIGNALED_INTERNALLY", "SIGNALED_INTERNALLY"
    SIGNALED_COLLECTIVITY = "SIGNALED_COLLECTIVITY", "SIGNALED_COLLECTIVITY"
    CONFIRMED_FIELD = "CONFIRMED_FIELD", "CONFIRMED_FIELD"
    INVALIDATED_FIELD = "INVALIDATED_FIELD", "INVALIDATED_FIELD"


class DetectionValidationStatus(models.TextChoices):
    DETECTED_NOT_VERIFIED = "DETECTED_NOT_VERIFIED", "DETECTED_NOT_VERIFIED"
    SUSPECT = "SUSPECT", "SUSPECT"
    LEGITIMATE = "LEGITIMATE", "LEGITIMATE"
    INVALIDATED = "INVALIDATED", "INVALIDATED"
    CONTROLLED = "CONTROLLED", "CONTROLLED"


class DetectionData(TimestampedModelMixin, UuidModelMixin, DeletableModelMixin):
    detection_control_status = models.CharField(
        max_length=DEFAULT_MAX_LENGTH,
        choices=DetectionControlStatus.choices,
    )
    detection_validation_status = models.CharField(
        max_length=DEFAULT_MAX_LENGTH,
        choices=DetectionValidationStatus.choices,
    )
    user_last_update = models.ForeignKey(
        User, related_name="detection_datas_last_updated", on_delete=models.CASCADE
    )
