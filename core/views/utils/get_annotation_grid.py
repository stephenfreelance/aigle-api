from collections import defaultdict
import json
from django.http import JsonResponse


from core.models.detection import Detection
from django.contrib.gis.geos import Polygon

from core.views.detection import DetectionFilter

from django.core.exceptions import BadRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import connection
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon

GRID_SIZE = 0.01


def serialize_to_feature_collection(grid_elements):
    features = []
    for element in grid_elements:
        features.append(
            {
                "type": "Feature",
                "geometry": json.loads(element["geometry"].geojson),
                "properties": {
                    "i": element["i"],
                    "j": element["j"],
                    "total": element["total"],
                    "reviewed": element["reviewed"],
                    "text": f'{element["i"]} | {element["j"]}\n{element["reviewed"]}/{element["total"]} revues',
                },
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def endpoint(request):
    polygon_requested = Polygon.from_bbox(
        (
            request.GET["swLng"],
            request.GET["swLat"],
            request.GET["neLng"],
            request.GET["neLat"],
        )
    )

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT
                ST_AsText(geom),
                i,
                j
            FROM
                ST_SquareGrid (
                    {GRID_SIZE},
                    ST_GeomFromText('{str(polygon_requested)}', 4326)
                )
        """)
        grid_raw = cursor.fetchall()
        grid = [(GEOSGeometry(row[0]), row[1], row[2]) for row in grid_raw]

    all_geometries = MultiPolygon([row[0] for row in grid])
    sw_lng, sw_lat, ne_lng, ne_lat = all_geometries.extent

    # we want to get all detections contained in the grid
    data_requested = request.GET.copy()

    data_requested["swLng"] = sw_lng
    data_requested["swLat"] = sw_lat
    data_requested["neLng"] = ne_lng
    data_requested["neLat"] = ne_lat

    filterset = DetectionFilter(
        data_requested, queryset=Detection.objects, request=request
    )

    if not filterset.is_valid():
        raise BadRequest(filterset.errors)

    queryset = filterset.qs.values_list(
        "id", "detection_data__detection_validation_status", "geometry"
    )
    detections_raw = queryset.all()

    # Initialize result container
    grid_items_total = defaultdict(int)
    grid_items_reviewed = defaultdict(int)

    # Iterate over detections and count occurrences in each grid cell
    for detection_raw in detections_raw:
        detection_centroid = detection_raw[2].centroid
        for cell, i, j in grid:
            if cell.contains(detection_centroid):
                grid_items_total[(i, j)] += 1

                if detection_raw[1] != "DETECTED_NOT_VERIFIED":
                    grid_items_reviewed[(i, j)] += 1

                break

    # Output results
    grid_with_counts = [
        {
            "geometry": cell,
            "i": i,
            "j": j,
            "total": grid_items_total.get((i, j), 0),
            "reviewed": grid_items_reviewed.get((i, j), 0),
        }
        for cell, i, j in grid
    ]

    return JsonResponse(serialize_to_feature_collection(grid_with_counts), safe=False)


URL = "get-annotation-grid/"
