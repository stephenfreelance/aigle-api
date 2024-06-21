from core.models.object_type import ObjectType
from core.models.object_type_category import ObjectTypeCategory
from core.serializers import UuidTimestampedModelSerializerMixin

from rest_framework import serializers

from core.serializers.utils.query import get_objects


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
        fields = ["name", "color", "object_type_categories_uuids"]

    object_type_categories_uuids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=True, write_only=True
    )

    def create(self, validated_data):
        object_type_categories_uuids = validated_data.pop(
            "object_type_categories_uuids", None
        )
        categories = get_objects(
            uuids=object_type_categories_uuids, model=ObjectTypeCategory
        )

        instance = ObjectType(**validated_data)
        instance.save()

        if categories:
            instance.categories.set(categories)

        instance.save()

        return instance

    def update(self, instance: ObjectTypeCategory, validated_data):
        object_type_categories_uuids = validated_data.pop(
            "object_type_categories_uuids", None
        )
        categories = get_objects(
            uuids=object_type_categories_uuids, model=ObjectTypeCategory
        )

        if categories is not None:
            instance.categories.set(categories)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance
