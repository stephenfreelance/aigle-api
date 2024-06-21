from common.views.base import BaseViewSetMixin
from django_filters import FilterSet, CharFilter

from django.db.models import Q

from core.models.geo_commune import GeoCommune
from core.serializers.geo_commune import GeoCommuneSerializer
from core.utils.permissions import AdminRolePermission


class GeoCommuneFilter(FilterSet):
    q = CharFilter(method="search")

    class Meta:
        model = GeoCommune
        fields = ["q"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(iso_code__icontains=value))


class GeoCommuneViewSet(BaseViewSetMixin[GeoCommune]):
    filterset_class = GeoCommuneFilter
    permission_classes = [AdminRolePermission]

    def get_serializer_class(self):
        return GeoCommuneSerializer

    def get_queryset(self):
        queryset = GeoCommune.objects.order_by("iso_code")
        return queryset.distinct()
