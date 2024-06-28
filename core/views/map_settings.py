from rest_framework.views import APIView
from rest_framework.response import Response

from core.contants.order_by import TILE_SETS_ORDER_BYS
from core.models.object_type import ObjectType
from core.models.tile_set import TileSet, TileSetStatus, TileSetType
from core.models.user import UserRole
from core.models.user_group import UserGroupRight
from core.serializers.map_settings import MapSettingsSerializer
from core.serializers.object_type import ObjectTypeSerializer
from core.serializers.tile_set import TileSetMinimalSerializer

from django.db.models import Q


class MapSettingsView(APIView):
    def get(self, request, format=None):
        tile_sets = TileSet.objects.filter(
            tile_set_status__in=[TileSetStatus.VISIBLE, TileSetStatus.HIDDEN]
        ).order_by(*TILE_SETS_ORDER_BYS)

        tile_sets_uuids_map = {}

        if request.user.user_role == UserRole.SUPER_ADMIN:
            tile_sets = tile_sets.all()
            object_types = ObjectType.objects.all()

            tile_sets_uuids_map = {
                tile_set.uuid: (
                    tile_set,
                    set(
                        [
                            UserGroupRight.WRITE,
                            UserGroupRight.ANNOTATE,
                            UserGroupRight.READ,
                        ]
                    ),
                    set(object_types),
                )
                for tile_set in tile_sets
            }

        if request.user.user_role != UserRole.SUPER_ADMIN:
            user_user_groups = request.user.user_user_groups.all()

            communes = []
            departments = []
            regions = []

            for user_user_group in user_user_groups:
                communes += user_user_group.user_group.communes.all()
                departments += user_user_group.user_group.departments.all()
                regions += user_user_group.user_group.regions.all()

                tile_sets = tile_sets.filter(
                    Q(
                        tile_set_type__in=[
                            TileSetType.INDICATIVE,
                            TileSetType.BACKGROUND,
                        ]
                    )
                    | Q(communes__id__in=[geo.id for geo in communes])
                    | Q(departments__id__in=[geo.id for geo in departments])
                    | Q(departments__communes__id__in=[geo.id for geo in communes])
                    | Q(regions__id__in=[geo.id for geo in regions])
                    | Q(regions__departments__id__in=[geo.id for geo in departments])
                    | Q(
                        regions__departments__communes__id__in=[
                            geo.id for geo in communes
                        ]
                    )
                ).distinct()

                object_types = ObjectType.objects.filter(
                    categories__in=user_user_group.user_group.object_type_categories.all()
                ).distinct()

                for tile_set in tile_sets:
                    if tile_set.uuid not in tile_sets_uuids_map:
                        tile_sets_uuids_map[tile_set.uuid] = (
                            tile_set,
                            set(user_user_group.user_group_rights),
                            set(object_types),
                        )
                        continue

                    tile_sets_uuids_map[tile_set.uuid][1].update(
                        tile_set.user_group_rights
                    )
                    tile_sets_uuids_map[tile_set.uuid][2].update(object_types)

        settings = []

        for tile_set, user_group_rights, object_types in tile_sets_uuids_map.values():
            settings.append(
                {
                    "tile_set": TileSetMinimalSerializer(tile_set).data,
                    "object_types": ObjectTypeSerializer(object_types, many=True).data,
                    "user_group_rights": user_group_rights,
                }
            )

        settings = MapSettingsSerializer(
            data={
                "settings": settings,
            }
        )

        settings.is_valid()

        return Response(settings.data)
