from django.db import models


class DeletableModelMixin(models.Model):
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True
