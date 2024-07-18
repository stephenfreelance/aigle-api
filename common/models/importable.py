from django.db import models

from common.constants.models import DEFAULT_MAX_LENGTH


class ImportableModelMixin(models.Model):
    batch_id = models.CharField(max_length=DEFAULT_MAX_LENGTH, null=True)
    import_id = models.IntegerField(null=True)

    class Meta:
        abstract = True
