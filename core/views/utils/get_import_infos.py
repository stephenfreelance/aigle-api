from typing import List
from django.http import JsonResponse
from rest_framework import serializers

from core.models.detection import DetectionSource
from core.models.detection_data import (
    DetectionControlStatus,
    DetectionPrescriptionStatus,
    DetectionValidationStatus,
)
from django.core.exceptions import PermissionDenied
from core.models.object_type import ObjectType
from core.models.tile_set import TileSet

from core.utils.string import normalize


class InfoImportsSerializer(serializers.Serializer):
    objectTypes = serializers.ListField(child=serializers.CharField())
    tileSets = serializers.ListField(child=serializers.CharField())
    detectionSources = serializers.ListField(child=serializers.CharField())
    detectionControlStatuses = serializers.ListField(child=serializers.CharField())
    detectionPrescriptionStatuses = serializers.ListField(child=serializers.CharField())
    detectionValidationStatuses = serializers.ListField(child=serializers.CharField())


def format_list(list_: List[List[str]], format_fn=None) -> List[str]:
    return [item[0] if not format_fn else format_fn(item[0]) for item in list_]


def endpoint(request):
    if request.user.user_role != request.user.SUPER_ADMIN:
        raise PermissionDenied(
            "Vous devez être super admin pour accéder à cette ressource"
        )

    object_types_names = ObjectType.objects.values_list("name").all()
    tile_sets_names = TileSet.objects.values_list("name").all()
    DetectionSource.choices
    DetectionControlStatus.choices
    DetectionPrescriptionStatus.choices
    DetectionValidationStatus.choices

    serializer = InfoImportsSerializer(
        data={
            "objectTypes": format_list(list(object_types_names), format_fn=normalize),
            "tileSets": format_list(list(tile_sets_names), format_fn=normalize),
            "detectionSources": format_list(DetectionSource.choices),
            "detectionControlStatuses": format_list(DetectionControlStatus.choices),
            "detectionPrescriptionStatuses": format_list(
                DetectionPrescriptionStatus.choices
            ),
            "detectionValidationStatuses": format_list(
                DetectionValidationStatus.choices
            ),
        }
    )
    serializer.is_valid()

    return JsonResponse(serializer.data)


URL = "imports-infos/"
