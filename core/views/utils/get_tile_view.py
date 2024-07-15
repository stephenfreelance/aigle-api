from django.http import JsonResponse

from rest_framework import serializers


from core.utils.data_permissions import get_user_tile_sets
from core.utils.filters import UuidInFilter


class EndpointSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    tile_set_uuids = UuidInFilter()


def endpoint(request):
    params_serializer = EndpointSerializer(data=request.GET)
    params_serializer.is_valid(raise_exception=True)

    get_user_tile_sets(
        user=request.user, filter_tile_set_uuid__in=params_serializer.tile_set_uuids
    )

    return JsonResponse({"lat": "lat"})


URL = "get-tile/"
