from rest_framework import serializers


class UuidTimestampedModelSerializerMixin(serializers.ModelSerializer):
    class Meta:
        fields = [
            "uuid",
            "created_at",
            "updated_at",
        ]

    uuid = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class EagerLoadingSerializerMixin:
    @classmethod
    def setup_eager_loading(cls, queryset):
        if hasattr(cls, "SELECT"):
            queryset = queryset.select_related(*cls.SELECT)

        if hasattr(cls, "PREFETCH"):
            queryset = queryset.prefetch_related(*cls.PREFETCH)

        return queryset
