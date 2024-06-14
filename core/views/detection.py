from common.views.base import BaseViewSetMixin


from core.models.detection import Detection
from core.serializers.detection import (
    DetectionDetailSerializer,
    DetectionInputSerializer,
    DetectionMinimalSerializer,
    DetectionUpdateSerializer,
)
from core.utils.filters import GeoBoundsFilter, UuidInFilter


class DetectionFilter(GeoBoundsFilter):
    objectTypesUuids = UuidInFilter(method="search_object_types_uuids")

    class Meta(GeoBoundsFilter.Meta):
        model = Detection
        fields = GeoBoundsFilter.Meta.fields + []

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
