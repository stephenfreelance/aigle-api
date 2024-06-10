from typing import List, Optional
from core.models.object_type import ObjectType
from core.models.object_type_category import ObjectTypeCategory
from core.serializers import UuidTimestampedModelSerializerMixin

from rest_framework import serializers

from core.serializers.object_type import ObjectTypeSerializer


class ObjectTypeCategorySerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = ObjectTypeCategory
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + ["name"]


class ObjectTypeCategoryDetailSerializer(ObjectTypeCategorySerializer):
    class Meta(ObjectTypeCategorySerializer.Meta):
        fields = ObjectTypeCategorySerializer.Meta.fields + ["object_types"]

    object_types = ObjectTypeSerializer(many=True, read_only=True)


class ObjectTypeCategoryInputSerializer(ObjectTypeCategorySerializer):
    class Meta(ObjectTypeCategorySerializer.Meta):
        fields = ["name", "object_types_uuids"]

    object_types_uuids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=True, write_only=True
    )

    def create(self, validated_data):
        object_types_uuids = validated_data.pop("object_types_uuids", None)
        object_types = get_object_types(object_types_uuids=object_types_uuids)

        instance = ObjectTypeCategory(**validated_data)
        instance.save()

        if object_types:
            instance.object_types.set(object_types)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance

    def update(self, instance: ObjectTypeCategory, validated_data):
        object_types_uuids = validated_data.pop("object_types_uuids", None)
        object_types = get_object_types(object_types_uuids=object_types_uuids)

        if object_types is not None:
            instance.object_types.set(object_types)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


# utils


def get_object_types(object_types_uuids: Optional[List[str]]):
    if object_types_uuids is None:
        return None

    # remove potential duplicates
    object_types_uuids = list(set(object_types_uuids))
    object_types = ObjectType.objects.filter(uuid__in=object_types_uuids)

    if len(object_types_uuids) != len(object_types):
        uuids_not_found = list(
            set(object_types_uuids)
            - set([object_type.uuid for object_type in object_types])
        )

        raise serializers.ValidationError(
            f"Some object types were not found, uuids: {", ".join(uuids_not_found)}"
        )

    return object_types
