from common.views.base import BaseViewSetMixin
from django.db.models import Q


from core.models.geo_region import GeoRegion
from core.serializers.geo_region import GeoRegionDetailSerializer, GeoRegionSerializer
from django_filters import FilterSet, CharFilter

from core.utils.permissions import AdminRolePermission


class GeoRegionFilter(FilterSet):
    q = CharFilter(method="search")

    class Meta:
        model = GeoRegion
        fields = ["q"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(insee_code__icontains=value)
        )


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
