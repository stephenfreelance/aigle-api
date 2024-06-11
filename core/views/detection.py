from common.views.base import BaseViewSetMixin


from core.models.detection import Detection
from core.serializers.detection import (
    DetectionDetailSerializer,
    DetectionInputSerializer,
    DetectionMinimalSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from core.utils.filters import GeoBoundsFilter


class DetectionFilter(GeoBoundsFilter):
    class Meta(GeoBoundsFilter.Meta):
        model = Detection
        fields = GeoBoundsFilter.Meta.fields + []


class DetectionViewSet(BaseViewSetMixin[Detection]):
    filterset_class = DetectionFilter

    def get_serializer_class(self):
        if self.action in ["create", "partial_update", "update"]:
            return DetectionInputSerializer

        detail = bool(self.request.query_params.get("detail"))

        if self.action in ["list"] and not detail:
            return DetectionMinimalSerializer

        return DetectionDetailSerializer

    def get_queryset(self):
        queryset = Detection.objects.order_by("-created_at")
        return queryset.distinct()
