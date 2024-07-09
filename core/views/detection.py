from common.views.base import BaseViewSetMixin

from operator import or_
from django.db.models import Q
from functools import reduce
from django_filters import FilterSet
from django_filters import (
    NumberFilter,
)
from django.contrib.gis.db.models.functions import Centroid
from core.contants.order_by import TILE_SETS_ORDER_BYS
from core.models.detection import Detection
from core.models.detection_data import DetectionControlStatus, DetectionValidationStatus
from core.models.tile_set import TileSet, TileSetType
from core.serializers.detection import (
    DetectionDetailSerializer,
    DetectionInputSerializer,
    DetectionMinimalSerializer,
    DetectionUpdateSerializer,
)
from core.utils.filters import ChoiceInFilter, UuidInFilter
from django.contrib.gis.geos import Polygon
from django.contrib.gis.db.models.functions import Intersection

from django.contrib.gis.db.models.aggregates import Union
from django.db.models import Count


class DetectionFilter(FilterSet):
    objectTypesUuids = UuidInFilter(method="search_object_types_uuids")
    tileSetsUuids = UuidInFilter(method="pass_")
    detectionValidationStatuses = ChoiceInFilter(
        field_name="detection_data__detection_validation_status",
        choices=DetectionValidationStatus.choices,
    )
    detectionControlStatuses = ChoiceInFilter(
        field_name="detection_data__detection_control_status",
        choices=DetectionControlStatus.choices,
    )

    neLat = NumberFilter(method="pass_")
    neLng = NumberFilter(method="pass_")

    swLat = NumberFilter(method="pass_")
    swLng = NumberFilter(method="pass_")

    def pass_(self, queryset, name, value):
        return queryset

    class Meta:
        model = Detection
        fields = ["neLat", "neLng", "swLat", "swLng", "tileSetsUuids"]
        geo_field = "geometry"

    def search_tile_sets_uuids(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        tile_sets_uuids = (
            self.data.get("tileSetsUuids").split(",")
            if self.data.get("tileSetsUuids")
            else []
        )

        # get geometry total

        # geomtery requested

        ne_lat = self.data.get("neLat")
        ne_lng = self.data.get("neLng")
        sw_lat = self.data.get("swLat")
        sw_lng = self.data.get("swLng")

        if not ne_lat or not ne_lng or not sw_lat or not sw_lng:
            return queryset

        polygon_requested = Polygon.from_bbox((sw_lng, sw_lat, ne_lng, ne_lat))
        polygon_requested.srid = 4326

        tile_sets = TileSet.objects
        tile_sets = tile_sets.annotate(
            union_geometry=Union("geo_zones__geometry"),
            intersection=Intersection("union_geometry", polygon_requested),
            geo_zones_count=Count("geo_zones"),
        )
        tile_sets = tile_sets.filter(
            uuid__in=tile_sets_uuids,
            tile_set_type__in=[TileSetType.BACKGROUND, TileSetType.PARTIAL],
        )
        tile_sets = tile_sets.filter(
            Q(intersection__isnull=False) | Q(geo_zones_count=0)
        )
        tile_sets = tile_sets.order_by(*TILE_SETS_ORDER_BYS).all()

        # Annotate the queryset with the centroid of the geometry
        queryset = queryset.annotate(centroid=Centroid("geometry"))

        wheres = []

        for i in range(len(tile_sets)):
            tile_set = tile_sets[i]
            previous_tile_sets = tile_sets[:i]

            if tile_set.intersection:
                where = Q(tile_set__uuid=tile_set.uuid) & Q(
                    centroid__intersects=tile_set.intersection
                )
            else:
                where = Q(tile_set__uuid=tile_set.uuid) & Q(
                    centroid__intersects=polygon_requested
                )

            for previous_tile_set in previous_tile_sets:
                where = where & ~Q(centroid__within=previous_tile_set.intersection)

            wheres.append(where)

            # if no geometry, we can stop the loop
            if not tile_set.intersection:
                break

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
        queryset = queryset.prefetch_related(
            "detection_object", "detection_object__object_type", "tile", "tile_set"
        ).select_related("detection_data")
        return queryset.distinct()
