from common.views.base import BaseViewSetMixin


from core.models.detection_object import DetectionObject
from core.serializers.detection_object import (
    DetectionObjectDetailSerializer,
    DetectionObjectSerializer,
)
from core.utils.filters import GeoBoundsFilter


class DetectionObjectFilter(GeoBoundsFilter):
    class Meta(GeoBoundsFilter.Meta):
        model = DetectionObject
        fields = GeoBoundsFilter.Meta.fields + []


class DetectionViewSet(BaseViewSetMixin[DetectionObject]):
    filterset_class = DetectionObjectFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DetectionObjectDetailSerializer

        return DetectionObjectSerializer

    def get_queryset(self):
        queryset = DetectionObject.objects.order_by("-detection__created_at")
        return queryset.distinct()
