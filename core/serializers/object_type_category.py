from typing import Dict, List, Optional
from core.models.object_type import ObjectType
from core.models.object_type_category import (
    ObjectTypeCategory,
    ObjectTypeCategoryObjectType,
)
from core.serializers import UuidTimestampedModelSerializerMixin

from rest_framework import serializers

from core.serializers.object_type import ObjectTypeSerializer


class ObjectTypeCategorySerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = ObjectTypeCategory
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + ["name"]


class ObjectTypeCategoryObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectTypeCategoryObjectType
        fields = ["object_type_category_object_type_status", "object_type"]

    object_type = ObjectTypeSerializer(read_only=True)


class ObjectTypeCategoryDetailSerializer(ObjectTypeCategorySerializer):
    class Meta(ObjectTypeCategorySerializer.Meta):
        fields = ObjectTypeCategorySerializer.Meta.fields + [
            "object_type_category_object_types"
        ]

    object_type_category_object_types = ObjectTypeCategoryObjectTypeSerializer(
        many=True, read_only=True
    )


class ObjectTypeCategoryObjectTypeInputSerializer(
    ObjectTypeCategoryObjectTypeSerializer
):
    class Meta(ObjectTypeCategoryObjectTypeSerializer.Meta):
        fields = ["object_type_category_object_type_status", "object_type_uuid"]

    object_type_uuid = serializers.UUIDField(write_only=True)


class ObjectTypeCategoryInputSerializer(ObjectTypeCategorySerializer):
    class Meta(ObjectTypeCategorySerializer.Meta):
        fields = ["name", "object_type_category_object_types"]

    object_type_category_object_types = ObjectTypeCategoryObjectTypeInputSerializer(
        many=True, required=False, allow_empty=True, write_only=True
    )

    def create(self, validated_data):
        object_type_category_object_types_raw = validated_data.pop(
            "object_type_category_object_types", None
        )

        instance = ObjectTypeCategory(**validated_data)
        instance.save()

        set_object_type_category_object_types(
            object_type_category=instance,
            object_type_category_object_types_raw=object_type_category_object_types_raw,
        )

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance

    def update(self, instance: ObjectTypeCategory, validated_data):
        object_type_category_object_types_raw = validated_data.pop(
            "object_type_category_object_types", None
        )
        set_object_type_category_object_types(
            object_type_category=instance,
            object_type_category_object_types_raw=object_type_category_object_types_raw,
        )

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


# utils


def set_object_type_category_object_types(
    object_type_category: ObjectTypeCategory,
    object_type_category_object_types_raw: Optional[List[Dict]],
) -> List[ObjectTypeCategoryObjectType]:
    if object_type_category_object_types_raw is None:
        return None

    object_type_category_uuids_statuses_map = {
        otcot["object_type_uuid"]: otcot["object_type_category_object_type_status"]
        for otcot in object_type_category_object_types_raw
    }
    object_types_uuids = list(object_type_category_uuids_statuses_map.keys())
    object_types = ObjectType.objects.filter(uuid__in=object_types_uuids)

    if len(object_types_uuids) != len(object_types):
        uuids_not_found = list(
            set(object_types_uuids)
            - set([object_type.uuid for object_type in object_types])
        )

        raise serializers.ValidationError(
            f"Some object types were not found, uuids: {
                ", ".join(uuids_not_found)}"
        )

    object_type_category_object_types = []

    for object_type in object_types:
        object_type_category_object_types.append(
            ObjectTypeCategoryObjectType(
                object_type_category=object_type_category,
                object_type=object_type,
                object_type_category_object_type_status=object_type_category_uuids_statuses_map[
                    object_type.uuid
                ],
            )
        )

    previous_object_type_category_object_types = (
        object_type_category.object_type_category_object_types.all()
    )
    previous_object_type_category_object_types.delete()
    ObjectTypeCategoryObjectType.objects.bulk_create(object_type_category_object_types)

    return object_type_category_object_types
