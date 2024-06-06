from rest_framework.viewsets import ModelViewSet
from common.views.countable import CountableModelViewSetMixin
from common.views.deletable import DeletableModelViewSetMixin
from django.db.models import Q


from core.models.geo_region import GeoRegion
from core.serializers.geo_region import GeoRegionDetailSerializer, GeoRegionSerializer
from django_filters import FilterSet, CharFilter


class GeoRegionFilter(FilterSet):
    q = CharFilter(method="search")

    class Meta:
        model = GeoRegion
        fields = ["q"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(insee_code__icontains=value)
        )


class GeoRegionViewSet(
    DeletableModelViewSetMixin[GeoRegion], CountableModelViewSetMixin, ModelViewSet
):
    lookup_field = "uuid"
    filterset_class = GeoRegionFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GeoRegionDetailSerializer

        return GeoRegionSerializer

    def get_queryset(self):
        queryset = GeoRegion.objects.order_by("insee_code")
        return queryset.distinct()

    def get_serializer_context(self):
        return {"request": self.request}
