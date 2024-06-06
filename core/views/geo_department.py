from rest_framework.viewsets import ModelViewSet
from common.views.countable import CountableModelViewSetMixin
from common.views.deletable import DeletableModelViewSetMixin

from django.db.models import Q

from core.models.geo_department import GeoDepartment
from core.serializers.geo_department import (
    GeoDepartmentDetailSerializer,
    GeoDepartmentSerializer,
)
from django_filters import FilterSet, CharFilter


class GeoDepartmentFilter(FilterSet):
    q = CharFilter(method="search")

    class Meta:
        model = GeoDepartment
        fields = ["q"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(insee_code__icontains=value)
        )


class GeoDepartmentViewSet(
    DeletableModelViewSetMixin[GeoDepartment], CountableModelViewSetMixin, ModelViewSet
):
    lookup_field = "uuid"
    filterset_class = GeoDepartmentFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GeoDepartmentDetailSerializer

        return GeoDepartmentSerializer

    def get_queryset(self):
        queryset = GeoDepartment.objects.order_by("insee_code")
        return queryset.distinct()

    def get_serializer_context(self):
        return {"request": self.request}
