from typing import List
from django.http import JsonResponse
from rest_framework import serializers

from core.models.detection import DetectionSource
from core.models.detection_data import (
    DetectionControlStatus,
    DetectionPrescriptionStatus,
    DetectionValidationStatus,
)
from core.models.object_type import ObjectType
from core.models.tile_set import TileSet
from django.db.models import Count

from core.utils.serializers import CommaSeparatedUUIDField
from core.utils.string import normalize

from django.db.models import Q


class EndpointSerializer(serializers.Serializer):
    detection_validation_status = serializers.ChoiceField(
        choices=DetectionValidationStatus.choices,
        required=True,
    )
    tile_sets_uuids = CommaSeparatedUUIDField()


class OutputSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    name = serializers.CharField()
    date = serializers.DateTimeField()
    detectionsCount = serializers.IntegerField(source="detections_count")


def endpoint(request):
    endpoint_serializer = EndpointSerializer(data=request.GET)
    endpoint_serializer.is_valid(raise_exception=True)

    queryset = TileSet.objects.filter(
        uuid__in=endpoint_serializer.validated_data["tile_sets_uuids"]
    )
    queryset = queryset.order_by("date")
    queryset = queryset.values("uuid", "name", "date").annotate(
        detections_count=Count(
            "detections",
            filter=Q(
                detections__detection_data__detection_validation_status=endpoint_serializer.validated_data[
                    "detection_validation_status"
                ]
            ),
        )
    )

    output_serializer = OutputSerializer(data=queryset.all(), many=True)
    output_serializer.is_valid()

    return JsonResponse(output_serializer.data, safe=False)


URL = "validation-status-evolution/"
