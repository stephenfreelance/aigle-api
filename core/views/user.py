from common.views.countable import CountableModelViewSetMixin
from core.models.user import UserRole
from django_filters import FilterSet, CharFilter, OrderingFilter, MultipleChoiceFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from common.views.deletable import DeletableModelViewSetMixin
from django.contrib.auth import get_user_model

from core.serializers.user import (
    UserSerializer
)
from rest_framework.response import Response

from rest_framework.decorators import action

from core.utils.permissions import AdminRolePermission

UserModel = get_user_model()


class UserFilter(FilterSet):
    email = CharFilter(lookup_expr='icontains')
    roles = MultipleChoiceFilter(
        field_name="user_role", choices=UserRole.choices)
    ordering = OrderingFilter(fields=(
        'email',
        'created_at',
        'updated_at'
    ))

    class Meta:
        model = UserModel
        fields = ['email']


class UserViewSet(DeletableModelViewSetMixin[UserModel], CountableModelViewSetMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    lookup_field = "uuid"
    serializer_class = UserSerializer
    filterset_class = UserFilter
    permission_classes = [AdminRolePermission]

    def get_queryset(self):
        queryset = UserModel.objects.order_by('-id')

        return queryset.distinct()

    def get_serializer_context(self):
        return {"request": self.request}
