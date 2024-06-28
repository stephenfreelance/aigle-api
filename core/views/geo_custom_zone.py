from common.views.base import BaseViewSetMixin


from core.models.geo_custom_zone import GeoCustomZone
from core.serializers.geo_custom_zone import (
    GeoCustomZoneDetailSerializer,
    GeoCustomZoneSerializer,
)
from django_filters import FilterSet, CharFilter

from core.utils.permissions import AdminRolePermission


class GeoCustomZoneFilter(FilterSet):
    q = CharFilter(method="search")

    class Meta:
        model = GeoCustomZone
        fields = ["q"]

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class GeoCustomZoneViewSet(BaseViewSetMixin[GeoCustomZone]):
    filterset_class = GeoCustomZoneFilter
    permission_classes = [AdminRolePermission]

    def get_serializer_class(self):
        if self.action in ["retrieve", "create", "partial_update", "update"]:
            return GeoCustomZoneDetailSerializer

        return GeoCustomZoneSerializer

    def get_queryset(self):
        queryset = GeoCustomZone.objects.order_by("name")
        return queryset.distinct()
