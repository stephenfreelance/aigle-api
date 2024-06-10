from common.views.base import BaseViewSetMixin
from django.db.models import Q


from django_filters import FilterSet, CharFilter

from core.models.object_type_category import ObjectTypeCategory
from core.serializers.object_type_category import (
    ObjectTypeCategoryDetailSerializer,
    ObjectTypeCategoryInputSerializer,
)
from core.utils.filters import UuidInFilter


class ObjectTypeCategoryFilter(FilterSet):
    q = CharFilter(method="search")
    objectTypesUuids = UuidInFilter(method="search_object_types_uuids")

    class Meta:
        model = ObjectTypeCategory
        fields = ["q"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value))

    def search_object_types_uuids(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(Q(object_types__uuid__in=value))


class ObjectTypeCategoryViewSet(
    BaseViewSetMixin[ObjectTypeCategory],
):
    filterset_class = ObjectTypeCategoryFilter

    def get_serializer_class(self):
        if self.action in ["create", "partial_update", "update"]:
            return ObjectTypeCategoryInputSerializer

        return ObjectTypeCategoryDetailSerializer

    def get_queryset(self):
        queryset = ObjectTypeCategory.objects.order_by("name")
        return queryset.distinct()

    def get_serializer_context(self):
        return {"request": self.request}
