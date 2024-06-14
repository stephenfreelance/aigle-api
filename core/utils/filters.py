from django_filters import (
    BaseInFilter,
    FilterSet,
    UUIDFilter,
    NumberFilter,
    ChoiceFilter,
)
from rest_framework.exceptions import ValidationError
from django.contrib.gis.geos import Polygon


class UuidInFilter(BaseInFilter, UUIDFilter):
    pass


class ChoiceInFilter(BaseInFilter, ChoiceFilter):
    pass


class GeoBoundsFilter(FilterSet):
    neLat = NumberFilter(method="filter_bounds")
    neLng = NumberFilter(method="filter_bounds")

    swLat = NumberFilter(method="filter_bounds")
    swLng = NumberFilter(method="filter_bounds")

    class Meta:
        fields = ["neLat", "neLng", "swLat", "swLng"]
        geo_field = "geometry"

    def filter_bounds(self, queryset, name, value):
        ne_lat = self.data.get("neLat")
        ne_lng = self.data.get("neLng")
        sw_lat = self.data.get("swLat")
        sw_lng = self.data.get("swLng")

        if any(coord is None for coord in [ne_lat, ne_lng, sw_lat, sw_lng]):
            raise ValidationError(
                "Vous devez spécifier tous les paramètres suivant pour filter"
                " par limite géographique: ne_lat,ne_lng,sw_lat,sw_lng"
            )

        bounding_box = Polygon.from_bbox((sw_lng, sw_lat, ne_lng, ne_lat))

        return queryset.filter(**{f"{self.Meta.geo_field}__intersects": bounding_box})
