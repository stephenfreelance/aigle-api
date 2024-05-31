from rest_framework.viewsets import ModelViewSet
from common.views.countable import CountableModelViewSetMixin
from common.views.deletable import DeletableModelViewSetMixin
from rest_framework.response import Response
from django_filters import FilterSet, CharFilter, OrderingFilter, MultipleChoiceFilter

from rest_framework.decorators import action
from django.db.models import Q

from core.models.geo_commune import GeoCommune
from core.serializers.geo_commune import GeoCommuneSerializer

class GeoCommuneFilter(FilterSet):
    q = CharFilter(method='search')
    
    class Meta:
        model = GeoCommune
        fields = [
            'q'
        ]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(iso_code__icontains=value)
        )


class GeoCommuneViewSet(DeletableModelViewSetMixin[GeoCommune], CountableModelViewSetMixin, ModelViewSet):
    lookup_field = "uuid"
    filterset_class = GeoCommuneFilter

    def get_serializer_class(self):
        return GeoCommuneSerializer

    def get_queryset(self):
        queryset = GeoCommune.objects.order_by('iso_code')
        return queryset.distinct()
    
    def get_serializer_context(self):
        return {"request": self.request}
