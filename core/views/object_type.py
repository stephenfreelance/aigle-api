from rest_framework.viewsets import ModelViewSet
from common.views.countable import CountableModelViewSetMixin
from common.views.deletable import DeletableModelViewSetMixin
from rest_framework.response import Response
from django.db.models import Q

from rest_framework.decorators import action

from core.models.object_type import ObjectType
from django_filters import FilterSet, CharFilter, OrderingFilter, MultipleChoiceFilter

from core.serializers.object_type import ObjectTypeSerializer

class ObjectTypeFilter(FilterSet):
    q = CharFilter(method='search')

    class Meta:
        model = ObjectType
        fields = [
            'q'
        ]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )

class ObjectTypeViewSet(DeletableModelViewSetMixin[ObjectType], CountableModelViewSetMixin, ModelViewSet):
    lookup_field = "uuid"
    filterset_class = ObjectTypeFilter
    serializer_class = ObjectTypeSerializer
    
    def get_queryset(self):
        queryset = ObjectType.objects.order_by('name')
        return queryset.distinct()
    
    def get_serializer_context(self):
        return {"request": self.request}
