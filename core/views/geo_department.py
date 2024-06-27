from common.views.base import BaseViewSetMixin

from django.db.models import Q

from core.models.geo_department import GeoDepartment
from core.serializers.geo_department import (
    GeoDepartmentDetailSerializer,
    GeoDepartmentSerializer,
)
from django_filters import FilterSet, CharFilter

from core.utils.permissions import AdminRolePermission
from django.db.models import Case, IntegerField, Value, When
from django.db.models.functions import Length


class GeoDepartmentFilter(FilterSet):
    q = CharFilter(method="search")

    class Meta:
        model = GeoDepartment
        fields = ["q"]

    def search(self, queryset, name, value):
        queryset = queryset.annotate(
            match_score=Case(
                When(name__iexact=value, then=Value(4)),
                When(insee_code__iexact=value, then=Value(3)),
                When(name__icontains=value, then=Value(2)),
                When(insee_code__icontains=value, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )

        return queryset.filter(
            Q(name__icontains=value) | Q(insee_code__icontains=value)
        ).order_by("-match_score", Length("name"))


class GeoDepartmentViewSet(BaseViewSetMixin[GeoDepartment]):
    filterset_class = GeoDepartmentFilter
    permission_classes = [AdminRolePermission]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GeoDepartmentDetailSerializer

        return GeoDepartmentSerializer

    def get_queryset(self):
        queryset = GeoDepartment.objects.order_by("insee_code")
        return queryset.distinct()
