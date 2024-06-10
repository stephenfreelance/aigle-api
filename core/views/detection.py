from common.views.base import BaseViewSetMixin


from core.models.detection import Detection
from core.serializers.detection import (
    DetectionDetailSerializer,
    DetectionInputSerializer,
)
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

        return DetectionDetailSerializer

    def get_queryset(self):
        queryset = Detection.objects.order_by("-created_at")
        return queryset.distinct()
