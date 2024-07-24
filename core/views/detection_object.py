from common.views.base import BaseViewSetMixin

from rest_framework.response import Response

from core.models.detection_object import DetectionObject
from core.serializers.detection_object import (
    DetectionObjectDetailSerializer,
    DetectionObjectHistorySerializer,
    DetectionObjectInputSerializer,
    DetectionObjectSerializer,
)
from rest_framework.decorators import action

from core.views.utils.save_user_position import save_user_position


class DetectionObjectViewSet(BaseViewSetMixin[DetectionObject]):
    def get_serializer_class(self):
        if self.action == "retrieve":
            return DetectionObjectDetailSerializer

        if self.action in ["partial_update", "update"]:
            return DetectionObjectInputSerializer

        if self.action == "history":
            return DetectionObjectHistorySerializer

        return DetectionObjectSerializer

    def get_queryset(self):
        queryset = DetectionObject.objects.order_by("-detections__tile_set__date")
        queryset = queryset.prefetch_related(
            "detections",
            "detections__tile",
            "detections__tile_set",
            "detections__detection_data",
            "object_type",
            "parcel",
            "parcel__commune",
        )
        return queryset.distinct()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        try:
            last_position = instance.detections.all()[0].geometry.centroid
            save_user_position(user=request.user, last_position=last_position)
        except Exception:
            pass

        return Response(serializer.data)

    @action(methods=["get"], detail=True)
    def history(self, request, uuid):
        queryset = self.get_queryset()
        detection_object = (
            queryset.prefetch_related("detections").filter(uuid=uuid).first()
        )
        SerializerClass = self.get_serializer_class()
        serializer = SerializerClass(
            detection_object, context={"request": self.request}
        )
        return Response(serializer.data)
