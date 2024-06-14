from common.views.base import BaseViewSetMixin
from django_filters import FilterSet, CharFilter

from django.db.models import Q

from core.models.tile_set import TileSet, TileSetScheme, TileSetStatus, TileSetType
from core.serializers.tile_set import TileSetSerializer
from core.utils.filters import ChoiceInFilter


class TileSetFilter(FilterSet):
    q = CharFilter(method="search")
    statuses = ChoiceInFilter(
        field_name="tile_set_status", choices=TileSetStatus.choices
    )
    schemes = ChoiceInFilter(
        field_name="tile_set_scheme", choices=TileSetScheme.choices
    )
    types = ChoiceInFilter(field_name="tile_set_type", choices=TileSetType.choices)

    class Meta:
        model = TileSet
        fields = ["q"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(url__icontains=value))


class TileSetViewSet(BaseViewSetMixin[TileSet]):
    filterset_class = TileSetFilter

    def get_serializer_class(self):
        return TileSetSerializer

    def get_queryset(self):
        queryset = TileSet.objects.order_by("-date")
        return queryset.distinct()

    def get_serializer_context(self):
        return {"request": self.request}
