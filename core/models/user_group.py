from django.db import models


from common.constants.models import DEFAULT_MAX_LENGTH
from common.models.deletable import DeletableModelMixin
from common.models.timestamped import TimestampedModelMixin
from common.models.uuid import UuidModelMixin
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model

from core.models.geo_commune import GeoCommune
from core.models.geo_department import GeoDepartment
from core.models.geo_region import GeoRegion
from core.models.object_type_category import ObjectTypeCategory

UserModel = get_user_model()


class UserGroup(TimestampedModelMixin, UuidModelMixin, DeletableModelMixin):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    communes = models.ManyToManyField(GeoCommune, related_name="user_groups")
    departments = models.ManyToManyField(GeoDepartment, related_name="user_groups")
    regions = models.ManyToManyField(GeoRegion, related_name="user_groups")
    object_type_categories = models.ManyToManyField(
        ObjectTypeCategory, related_name="user_groups"
    )


class UserGroupRight(models.TextChoices):
    WRITE = "WRITE", "WRITE"
    ANNOTATE = "ANNOTATE", "ANNOTATE"
    READ = "READ", "READ"


class UserUserGroup(TimestampedModelMixin):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "user_group"], name="user_user_group_unique"
            ),
        ]

    user_group_rights = ArrayField(
        models.CharField(
            max_length=DEFAULT_MAX_LENGTH,
            choices=UserGroupRight.choices,
        )
    )
    user = models.ForeignKey(
        UserModel, related_name="user_user_groups", on_delete=models.CASCADE
    )
    user_group = models.ForeignKey(
        UserGroup, related_name="user_user_groups", on_delete=models.CASCADE
    )
