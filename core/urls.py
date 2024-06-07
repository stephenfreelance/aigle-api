from core.views.geo_commune import GeoCommuneViewSet
from core.views.geo_department import GeoDepartmentViewSet
from core.views.geo_region import GeoRegionViewSet
from core.views.map_settings import MapSettingsView
from core.views.object_type import ObjectTypeViewSet
from core.views.object_type_category import ObjectTypeCategoryViewSet
from core.views.tile_set import TileSetViewSet
from core.views.user import UserViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter()
router.register("users", UserViewSet, basename="UserViewSet")

router.register("geo/commune", GeoCommuneViewSet, basename="GeoCommuneViewSet")
router.register("geo/department", GeoDepartmentViewSet, basename="GeoDepartmentViewSet")
router.register("geo/region", GeoRegionViewSet, basename="GeoRegionViewSet")

router.register("object-type", ObjectTypeViewSet, basename="ObjectTypeViewSet")
router.register(
    "object-type-category",
    ObjectTypeCategoryViewSet,
    basename="ObjectTypeCategoryViewSet",
)

router.register("tile-set", TileSetViewSet, basename="TileSetViewSet")

urlpatterns = router.urls
urlpatterns += [
    path("map-settings/", MapSettingsView.as_view(), name="MapSettingsView")
]
