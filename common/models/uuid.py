from django.db import models
import uuid


class UuidModelMixin(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["uuid"], name="%(class)s_uuid_idx"),
        ]
