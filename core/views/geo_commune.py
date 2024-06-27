from common.views.base import BaseViewSetMixin
from django_filters import FilterSet, CharFilter

from django.db.models import Q

from core.models.geo_commune import GeoCommune
from core.serializers.geo_commune import (
    GeoCommuneDetailSerializer,
    GeoCommuneSerializer,
)
from core.utils.permissions import AdminRolePermission
from django.db.models import Case, IntegerField, Value, When
from django.db.models.functions import Length


class GeoCommuneFilter(FilterSet):
    q = CharFilter(method="search")

    class Meta:
        model = GeoCommune
        fields = ["q"]

    def search(self, queryset, name, value):
        queryset = queryset.annotate(
            match_score=Case(
                When(name__iexact=value, then=Value(4)),
                When(iso_code__iexact=value, then=Value(3)),
                When(name__icontains=value, then=Value(2)),
                When(iso_code__icontains=value, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )

        return queryset.filter(
            Q(name__icontains=value) | Q(iso_code__icontains=value)
        ).order_by("-match_score", Length("name"))


class GeoCommuneViewSet(BaseViewSetMixin[GeoCommune]):
    filterset_class = GeoCommuneFilter
    permission_classes = [AdminRolePermission]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GeoCommuneDetailSerializer

        return GeoCommuneSerializer

    def get_queryset(self):
        queryset = GeoCommune.objects.order_by("iso_code")
        return queryset.distinct()
