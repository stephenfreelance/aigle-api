from typing import List, Optional


from rest_framework import serializers
from django.db import models


def get_objects(uuids: Optional[List[str]], model: models.Model):
    if uuids is None:
        return None

    # remove potential duplicates
    uuids = list(set(uuids))
    objects = model.objects.filter(uuid__in=uuids).all()

    if len(uuids) != len(objects):
        uuids_not_found = list(set(uuids) - set([object_.uuid for object_ in objects]))

        raise serializers.ValidationError(
            f"Some objects (type: {model.__name__}) were not found, uuids: {
                ", ".join(uuids_not_found)}"
        )

    return objects
