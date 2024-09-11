from rest_framework.response import Response
from common.views.base import BaseViewSetMixin


from rest_framework import serializers
from core.contants.order_by import GEO_CUSTOM_ZONES_ORDER_BYS
from core.models.geo_custom_zone import GeoCustomZone, GeoCustomZoneStatus
from core.serializers.geo_custom_zone import (
    GeoCustomZoneGeoFeatureSerializer,
    GeoCustomZoneSerializer,
)
from django_filters import FilterSet, CharFilter

from rest_framework.decorators import action

from core.utils.permissions import AdminRolePermission
from django.contrib.gis.geos import Polygon
from django.contrib.gis.db.models.functions import Intersection


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
            if self.request.GET.get("geometry"):
                return GeoCustomZoneGeoFeatureSerializer

        return GeoCustomZoneSerializer

    def get_queryset(self):
        queryset = GeoCustomZone.objects.order_by(*GEO_CUSTOM_ZONES_ORDER_BYS)

        return queryset
