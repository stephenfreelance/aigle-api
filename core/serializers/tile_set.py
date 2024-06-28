from core.models.geo_commune import GeoCommune
from core.models.geo_department import GeoDepartment
from core.models.geo_region import GeoRegion
from core.models.object_type_category import ObjectTypeCategory
from core.models.tile_set import TileSet
from core.models.user_group import UserGroup
from core.serializers import UuidTimestampedModelSerializerMixin
from core.serializers.geo_commune import GeoCommuneSerializer
from core.serializers.geo_department import GeoDepartmentSerializer
from core.serializers.geo_region import GeoRegionSerializer
from rest_framework_gis.fields import GeometryField

from rest_framework import serializers

from core.serializers.utils.query import get_objects


class TileSetMinimalSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = TileSet
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "name",
            "url",
            "tile_set_status",
            "tile_set_scheme",
            "tile_set_type",
            "date",
        ]


class TileSetSerializer(TileSetMinimalSerializer):
    class Meta(TileSetMinimalSerializer.Meta):
        model = TileSet
        fields = TileSetMinimalSerializer.Meta.fields + [
            "communes",
            "departments",
            "regions",
        ]

    communes = GeoCommuneSerializer(many=True, read_only=True)
    departments = GeoDepartmentSerializer(many=True, read_only=True)
    regions = GeoRegionSerializer(many=True, read_only=True)


class TileSetDetailSerializer(TileSetSerializer):
    class Meta(TileSetSerializer.Meta):
        fields = TileSetSerializer.Meta.fields + ["geometry"]

    geometry = GeometryField(read_only=True)


class TileSetInputSerializer(TileSetSerializer):
    class Meta(TileSetSerializer.Meta):
        fields = [
            "name",
            "url",
            "tile_set_status",
            "tile_set_scheme",
            "tile_set_type",
            "date",
            "communes_uuids",
            "departments_uuids",
            "regions_uuids",
        ]

    communes_uuids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=True, write_only=True
    )
    departments_uuids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=True, write_only=True
    )
    regions_uuids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=True, write_only=True
    )

    def create(self, validated_data):
        communes_uuids = validated_data.pop("communes_uuids", None)
        communes = get_objects(uuids=communes_uuids, model=GeoCommune)

        departments_uuids = validated_data.pop("departments_uuids", None)
        departments = get_objects(uuids=departments_uuids, model=GeoDepartment)

        regions_uuids = validated_data.pop("regions_uuids", None)
        regions = get_objects(uuids=regions_uuids, model=GeoRegion)

        object_type_categories_uuids = validated_data.pop(
            "object_type_categories_uuids", None
        )
        object_type_categories = get_objects(
            uuids=object_type_categories_uuids, model=ObjectTypeCategory
        )

        instance = TileSet(
            **validated_data,
        )

        instance.save()

        if communes:
            instance.communes.set(communes)

        if departments:
            instance.departments.set(departments)

        if regions:
            instance.regions.set(regions)

        if object_type_categories:
            instance.object_type_categories.set(object_type_categories)

        instance.save()

        return instance

    def update(self, instance: UserGroup, validated_data):
        communes_uuids = validated_data.pop("communes_uuids", None)
        communes = get_objects(uuids=communes_uuids, model=GeoCommune)

        departments_uuids = validated_data.pop("departments_uuids", None)
        departments = get_objects(uuids=departments_uuids, model=GeoDepartment)

        regions_uuids = validated_data.pop("regions_uuids", None)
        regions = get_objects(uuids=regions_uuids, model=GeoRegion)

        object_type_categories_uuids = validated_data.pop(
            "object_type_categories_uuids", None
        )
        object_type_categories = get_objects(
            uuids=object_type_categories_uuids, model=ObjectTypeCategory
        )

        if communes is not None:
            instance.communes.set(communes)

        if departments is not None:
            instance.departments.set(departments)

        if regions is not None:
            instance.regions.set(regions)

        if object_type_categories is not None:
            instance.object_type_categories.set(object_type_categories)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance
