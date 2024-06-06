from typing import List, Optional
from core.models.object_type import ObjectType
from core.models.object_type_category import ObjectTypeCategory
from core.serializers import UuidTimestampedModelSerializerMixin

from rest_framework import serializers


class ObjectTypeSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = ObjectType
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + ["name", "color"]


class ObjectTypeDetailSerializer(ObjectTypeSerializer):
    from core.serializers.object_type_category import ObjectTypeCategorySerializer

    class Meta(ObjectTypeSerializer.Meta):
        fields = ObjectTypeSerializer.Meta.fields + ["categories"]

    categories = ObjectTypeCategorySerializer(many=True, read_only=True)


class ObjectTypeInputSerializer(ObjectTypeDetailSerializer):
    class Meta(ObjectTypeDetailSerializer.Meta):
        fields = ["name", "color", "categories_uuids"]

    categories_uuids = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )

    def create(self, validated_data):
        categories_uuids = validated_data.pop("categories_uuids", None)
        categories = get_categories(categories_uuids=categories_uuids)

        instance = ObjectType(**validated_data)
        instance.save()

        if categories:
            instance.categories.set(categories)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance

    def update(self, instance: ObjectTypeCategory, validated_data):
        categories_uuids = validated_data.pop("categories_uuids", None)
        categories = get_categories(categories_uuids=categories_uuids)

        if categories is not None:
            instance.categories.set(categories)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


def get_categories(categories_uuids: Optional[List[str]]):
    if categories_uuids is None:
        return None

    # remove potential duplicates
    categories_uuids = list(set(categories_uuids))
    categories = ObjectTypeCategory.objects.filter(uuid__in=categories_uuids)

    if len(categories_uuids) != len(categories):
        uuids_not_found = list(
            set(categories_uuids) - set([category.uuid for category in categories])
        )

        raise serializers.ValidationError(
            f"Some categories were not found, uuids: {", ".join(uuids_not_found)}"
        )

    return categories
