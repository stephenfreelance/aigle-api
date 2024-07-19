from core.models.object_type import ObjectType
from core.models.object_type_category import ObjectTypeCategory
from core.serializers import UuidTimestampedModelSerializerMixin

from rest_framework import serializers


class ObjectTypeSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = ObjectType
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "name",
            "color",
            "prescription_duration_years",
        ]


class ObjectTypeDetailSerializer(ObjectTypeSerializer):
    class Meta(ObjectTypeSerializer.Meta):
        fields = ObjectTypeSerializer.Meta.fields + ["categories"]

    categories = serializers.SerializerMethodField(read_only=True)

    def get_categories(self, obj):
        from core.serializers.object_type_category import ObjectTypeCategorySerializer

        return ObjectTypeCategorySerializer(
            [
                object_type_category_object_type.object_type_category
                for object_type_category_object_type in obj.object_type_category_object_types.all()
            ],
            many=True,
            read_only=True,
        ).data


class ObjectTypeInputSerializer(ObjectTypeDetailSerializer):
    class Meta(ObjectTypeDetailSerializer.Meta):
        fields = [
            "name",
            "color",
            "prescription_duration_years",
        ]

    def create(self, validated_data):
        instance = ObjectType(**validated_data)
        instance.save()

        return instance

    def update(self, instance: ObjectTypeCategory, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance
