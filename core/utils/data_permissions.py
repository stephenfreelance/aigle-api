from core.contants.order_by import TILE_SETS_ORDER_BYS
from core.models.tile_set import TileSet, TileSetStatus, TileSetType
from core.models.user import UserRole
from core.models.user_group import UserUserGroup
from django.contrib.gis.db.models.functions import Intersection
from django.db.models import Q
from django.db.models import Count

from django.contrib.gis.db.models.aggregates import Union


def get_user_tile_sets(
    user, filter_tile_set_status__in=None, filter_tile_set_type__in=None, order_bys=None
):
    if filter_tile_set_status__in is None:
        filter_tile_set_status__in = [TileSetStatus.VISIBLE, TileSetStatus.HIDDEN]

    if filter_tile_set_type__in is None:
        filter_tile_set_type__in = [
            TileSetType.INDICATIVE,
            TileSetType.PARTIAL,
            TileSetType.BACKGROUND,
        ]

    if order_bys is None:
        order_bys = TILE_SETS_ORDER_BYS

    if user.user_role != UserRole.SUPER_ADMIN:
        user_user_groups_with_geo_union = UserUserGroup.objects.filter(
            user=user
        ).prefetch_related("user_group__object_type_categories__object_types")
        user_user_groups_with_geo_union = user_user_groups_with_geo_union.annotate(
            geo_union=Union("user_group__geo_zones__geometry")
        )

        final_union = user_user_groups_with_geo_union.aggregate(
            total_geo_union=Union("geo_union")
        )["total_geo_union"]
        intersection = Intersection("union_geometry", final_union)
    else:
        intersection = Union("geo_zones__geometry")

    tile_sets = TileSet.objects.filter(
        tile_set_status__in=filter_tile_set_status__in,
        tile_set_type__in=filter_tile_set_type__in,
    ).order_by(*order_bys)
    tile_sets = tile_sets.annotate(
        union_geometry=Union("geo_zones__geometry"),
        intersection=intersection,
        geo_zones_count=Count("geo_zones"),
    )

    tile_sets = tile_sets.filter(
        Q(intersection__isnull=False) | Q(geo_zones_count=0)
    ).distinct()

    return tile_sets
