from common.views.base import BaseViewSetMixin


from core.models.detection_object import DetectionObject
from core.serializers.detection_object import (
    DetectionObjectDetailSerializer,
    DetectionObjectInputSerializer,
    DetectionObjectSerializer,
)


class DetectionObjectViewSet(BaseViewSetMixin[DetectionObject]):
    def get_serializer_class(self):
        if self.action == "retrieve":
            return DetectionObjectDetailSerializer

        if self.action in ["partial_update", "update"]:
            return DetectionObjectInputSerializer

        return DetectionObjectSerializer

    def get_queryset(self):
        queryset = DetectionObject.objects.order_by("-detections__tile_set__date")
        return queryset.distinct()
