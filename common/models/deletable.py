from django.db import models


class DeletableModelMixin(models.Model):
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
