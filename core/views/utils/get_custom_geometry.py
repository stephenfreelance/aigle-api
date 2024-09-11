from django.http import JsonResponse

from rest_framework import serializers
from rest_framework.response import Response


from core.contants.order_by import GEO_CUSTOM_ZONES_ORDER_BYS
from core.models.geo_custom_zone import GeoCustomZone, GeoCustomZoneStatus
from core.serializers.geo_custom_zone import GeoCustomZoneGeoFeatureSerializer
from core.utils.data_permissions import get_user_tile_sets
from core.utils.filters import UuidInFilter
from django.contrib.gis.geos import Polygon
from django.contrib.gis.db.models.functions import Intersection


class GeometrySerializer(serializers.Serializer):
    neLat = serializers.FloatField()
    neLng = serializers.FloatField()
    swLat = serializers.FloatField()
    swLng = serializers.FloatField()

    uuids = serializers.CharField(required=False, allow_null=True)


def endpoint(request):
    geometry_serializer = GeometrySerializer(data=request.GET)
    geometry_serializer.is_valid(raise_exception=True)

    polygon_requested = Polygon.from_bbox(
        (
            geometry_serializer.data["swLng"],
            geometry_serializer.data["swLat"],
            geometry_serializer.data["neLng"],
            geometry_serializer.data["neLat"],
        )
    )
    polygon_requested.srid = 4326

    queryset = GeoCustomZone.objects.order_by(*GEO_CUSTOM_ZONES_ORDER_BYS)

    if geometry_serializer.data.get("uuids"):
        try:
            queryset = queryset.filter(
                uuid__in=geometry_serializer.data["uuids"].split(",")
            )
        except:
            pass

    queryset = queryset.filter(geo_custom_zone_status=GeoCustomZoneStatus.ACTIVE)
    queryset = queryset.filter(geometry__intersects=polygon_requested)
    queryset = queryset.values(
        "uuid",
        "name",
        "color",
        "geo_custom_zone_status",
    )
    queryset = queryset.annotate(geometry=Intersection("geometry", polygon_requested))

    serializer = GeoCustomZoneGeoFeatureSerializer(data=queryset.all(), many=True)
    serializer.is_valid()

    return JsonResponse(serializer.data)


URL = "get-custom-geometry/"
