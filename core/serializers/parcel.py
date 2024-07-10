from core.models.parcel import Parcel
from core.serializers import UuidTimestampedModelSerializerMixin


class ParcelMinimalSerializer(UuidTimestampedModelSerializerMixin):
    class Meta(UuidTimestampedModelSerializerMixin.Meta):
        model = Parcel
        fields = UuidTimestampedModelSerializerMixin.Meta.fields + [
            "id_parcellaire",
            "prefix",
            "section",
            "num_parcel",
        ]


class ParcelSerializer(ParcelMinimalSerializer):
    class Meta(ParcelMinimalSerializer.Meta):
        fields = ParcelMinimalSerializer.Meta.fields + [
            "geometry",
        ]
