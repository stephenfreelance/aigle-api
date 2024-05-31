from core.models.object_type import ObjectType
from core.serializers import UuidTimestampedModelSerializerMixin

from rest_framework import serializers


class ObjectTypeSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = ObjectType
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "name",
            "color"
        ]
    