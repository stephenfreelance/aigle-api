from common.views.countable import CountableModelViewSetMixin
from core.models.user import UserRole
from django_filters import FilterSet, CharFilter, OrderingFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, UpdateModelMixin
from common.views.deletable import DeletableModelViewSetMixin
from django.contrib.auth import get_user_model

from core.serializers.user import UserInputSerializer, UserSerializer


from core.utils.filters import ChoiceInFilter
from core.utils.permissions import AdminRolePermission

UserModel = get_user_model()


class UserFilter(FilterSet):
    email = CharFilter(lookup_expr="icontains")
    roles = ChoiceInFilter(field_name="user_role", choices=UserRole.choices)
    ordering = OrderingFilter(fields=("email", "created_at", "updated_at"))

    class Meta:
        model = UserModel
        fields = ["email"]


class UserViewSet(
    DeletableModelViewSetMixin[UserModel],
    CountableModelViewSetMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    lookup_field = "uuid"
    filterset_class = UserFilter
    permission_classes = [AdminRolePermission]

    def get_serializer_class(self):
        if self.action == "update":
            return UserInputSerializer

        return UserSerializer

    def get_queryset(self):
        queryset = UserModel.objects.order_by("-id")

        return queryset.distinct()

    def get_serializer_context(self):
        return {"request": self.request}
