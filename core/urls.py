from core.views.geo_commune import GeoCommuneViewSet
from core.views.geo_department import GeoDepartmentViewSet
from core.views.geo_region import GeoRegionViewSet
from core.views.object_type import ObjectTypeViewSet
from core.views.user import UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("users", UserViewSet, basename="UserViewSet")

router.register("geo/commune", GeoCommuneViewSet, basename="GeoCommuneViewSet")
router.register("geo/department", GeoDepartmentViewSet, basename="GeoDepartmentViewSet")
router.register("geo/region", GeoRegionViewSet, basename="GeoRegionViewSet")

router.register("object-type", ObjectTypeViewSet, basename="ObjectTypeViewSet")

urlpatterns = router.urls
