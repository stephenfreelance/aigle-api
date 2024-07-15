from common.views.base import BaseViewSetMixin

from operator import or_
from django.db.models import Q
from functools import reduce
from django_filters import FilterSet
from django_filters import NumberFilter, ChoiceFilter
from django.contrib.gis.db.models.functions import Centroid
from core.models.detection import Detection
from core.models.detection_data import (
    DetectionControlStatus,
    DetectionPrescriptionStatus,
    DetectionValidationStatus,
)
from core.models.tile_set import TileSetType
from core.serializers.detection import (
    DetectionDetailSerializer,
    DetectionInputSerializer,
    DetectionMinimalSerializer,
    DetectionUpdateSerializer,
)
from core.utils.data_permissions import get_user_tile_sets
from core.utils.filters import ChoiceInFilter, UuidInFilter
from django.contrib.gis.geos import Polygon

BOOLEAN_CHOICES = (("false", "False"), ("true", "True"), ("null", "Null"))


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
    detectionPrescriptionStatuses = ChoiceInFilter(
        field_name="detection_data__detection_prescription_status",
        choices=DetectionControlStatus.choices,
    )

    neLat = NumberFilter(method="pass_")
    neLng = NumberFilter(method="pass_")

    swLat = NumberFilter(method="pass_")
    swLng = NumberFilter(method="pass_")

    score = NumberFilter(field_name="score", lookup_expr="gte")
    prescripted = ChoiceFilter(choices=BOOLEAN_CHOICES, method="filter_prescripted")

    def pass_(self, queryset, name, value):
        return queryset

    class Meta:
        model = Detection
        fields = ["neLat", "neLng", "swLat", "swLng", "tileSetsUuids"]
        geo_field = "geometry"

    def search_tile_sets_uuids(self, queryset, name, value):
        return queryset

    def filter_prescripted(self, queryset, name, value):
        if value == "null":
            return queryset

        if value == "true":
            return queryset.filter(
                detection_data__detection_prescription_status=DetectionPrescriptionStatus.PRESCRIBED
            )

        return queryset.filter(
            Q(
                detection_data__detection_prescription_status=DetectionPrescriptionStatus.NOT_PRESCRIBED
            )
            | Q(detection_data__detection_prescription_status=None)
        )

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

        tile_sets, global_geometry = get_user_tile_sets(
            user=self.request.user,
            filter_tile_set_type__in=[TileSetType.PARTIAL, TileSetType.BACKGROUND],
            filter_tile_set_intersects_geometry=polygon_requested,
            filter_tile_set_uuid__in=tile_sets_uuids,
        )

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
                if global_geometry:
                    where = (
                        Q(tile_set__uuid=tile_set.uuid)
                        & Q(centroid__intersects=polygon_requested)
                        & Q(centroid__within=global_geometry)
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
