from rest_framework.viewsets import ModelViewSet
from common.views.countable import CountableModelViewSetMixin
from common.views.deletable import DeletableModelViewSetMixin
from django.db.models import Q


from core.models.object_type import ObjectType
from django_filters import FilterSet, CharFilter

from core.serializers.object_type import (
    ObjectTypeDetailSerializer,
    ObjectTypeInputSerializer,
)
from core.utils.filters import UuidInFilter


class ObjectTypeFilter(FilterSet):
    q = CharFilter(method="search")
    objectTypeCategoriesUuids = UuidInFilter(
        method="search_object_type_categories_uuids"
    )

    class Meta:
        model = ObjectType
        fields = ["q"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value))

    def search_object_type_categories_uuids(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(Q(categories__uuid__in=value))


class ObjectTypeViewSet(
    DeletableModelViewSetMixin[ObjectType], CountableModelViewSetMixin, ModelViewSet
):
    lookup_field = "uuid"
    filterset_class = ObjectTypeFilter

    def get_serializer_class(self):
        if self.action in ["create", "partial_update", "update"]:
            return ObjectTypeInputSerializer

        return ObjectTypeDetailSerializer

    def get_queryset(self):
        queryset = ObjectType.objects.order_by("name")
        return queryset.distinct()

    def get_serializer_context(self):
        return {"request": self.request}
