from common.views.base import BaseViewSetMixin
from django.db.models import Q


from core.models.geo_region import GeoRegion
from core.serializers.geo_region import GeoRegionDetailSerializer, GeoRegionSerializer
from django_filters import FilterSet, CharFilter

from core.utils.permissions import AdminRolePermission

from django.db.models import Case, IntegerField, Value, When
from django.db.models.functions import Length


class GeoRegionFilter(FilterSet):
    q = CharFilter(method="search")

    class Meta:
        model = GeoRegion
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


class GeoRegionViewSet(BaseViewSetMixin[GeoRegion]):
    filterset_class = GeoRegionFilter
    permission_classes = [AdminRolePermission]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GeoRegionDetailSerializer

        return GeoRegionSerializer

    def get_queryset(self):
        queryset = GeoRegion.objects.order_by("insee_code")
        return queryset.distinct()
