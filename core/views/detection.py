from common.views.base import BaseViewSetMixin

from operator import or_
from django.db.models import Q
from functools import reduce

from django.contrib.gis.db.models.functions import Centroid
from core.contants.order_by import TILE_SETS_ORDER_BYS
from core.models.detection import Detection
from core.models.tile_set import TileSet, TileSetType
from core.serializers.detection import (
    DetectionDetailSerializer,
    DetectionInputSerializer,
    DetectionMinimalSerializer,
    DetectionUpdateSerializer,
)
from core.utils.filters import GeoBoundsFilter, UuidInFilter


class DetectionFilter(GeoBoundsFilter):
    objectTypesUuids = UuidInFilter(method="search_object_types_uuids")
    tileSetsUuids = UuidInFilter(method="search_tile_sets_uuids")

    class Meta(GeoBoundsFilter.Meta):
        model = Detection
        fields = GeoBoundsFilter.Meta.fields + []

    def search_tile_sets_uuids(self, queryset, name, value):
        if not value:
            return queryset

        tile_sets_uuids = value

        tile_sets = (
            TileSet.objects.filter(
                uuid__in=tile_sets_uuids,
                tile_set_type__in=[TileSetType.BACKGROUND, TileSetType.PARTIAL],
            )
            .order_by(*TILE_SETS_ORDER_BYS)
            .all()
        )

        # Annotate the queryset with the centroid of the geometry
        queryset = queryset.annotate(centroid=Centroid("geometry"))

        wheres = []

        for i in range(len(tile_sets)):
            tile_set = tile_sets[i]
            previous_tile_sets = tile_sets[:i]

            where = Q(tile_set__uuid=tile_set.uuid) & Q(
                centroid__within=tile_set.geometry
            )

            for previous_tile_set in previous_tile_sets:
                where = where & ~Q(centroid__within=previous_tile_set.geometry)

            wheres.append(where)

        if len(wheres) == 1:
            return queryset.filter(wheres[0])

        return queryset.filter(reduce(or_, wheres))

    def search_object_types_uuids(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(detection_object__object_type__uuid__in=value)


class DetectionViewSet(BaseViewSetMixin[Detection]):
    filterset_class = DetectionFilter

    def get_serializer_class(self):
        if self.action in ["create"]:
            return DetectionInputSerializer

        if self.action in ["partial_update", "update"]:
            return DetectionUpdateSerializer

        detail = bool(self.request.query_params.get("detail"))

        if self.action in ["list"] and not detail:
            return DetectionMinimalSerializer

        return DetectionDetailSerializer

    def get_queryset(self):
        queryset = Detection.objects.order_by("-created_at")
        return queryset.distinct()
