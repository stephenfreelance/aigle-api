from django.db import models


from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin
from core.models.object_type import ObjectType


class DetectionObject(TimestampedModelMixin, UuidModelMixin, DeletableModelMixin):
    address = models.CharField(max_length=DEFAULT_MAX_LENGTH, null=True)
    object_type = models.ForeignKey(
        ObjectType, related_name="detected_objects", on_delete=models.CASCADE
    )
