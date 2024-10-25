from common.views.base import BaseViewSetMixin
from core.models.user import UserRole
from django_filters import FilterSet, CharFilter, OrderingFilter
from django.contrib.auth import get_user_model

from core.serializers.user import UserInputSerializer, UserSerializer


from core.utils.filters import ChoiceInFilter
from core.utils.permissions import MODIFY_ACTIONS, AdminRolePermission

UserModel = get_user_model()


class UserFilter(FilterSet):
    email = CharFilter(lookup_expr="icontains")
    roles = ChoiceInFilter(field_name="user_role", choices=UserRole.choices)
    ordering = OrderingFilter(fields=("email", "created_at", "updated_at"))

    class Meta:
        model = UserModel
        fields = ["email"]


class UserViewSet(
    BaseViewSetMixin[UserModel],
):
    lookup_field = "uuid"
    filterset_class = UserFilter
    permission_classes = [AdminRolePermission]

    def get_serializer_class(self):
        if self.action in MODIFY_ACTIONS:
            return UserInputSerializer

        return UserSerializer

    def get_queryset(self):
        queryset = UserModel.objects.order_by("-id")

        if self.request.user.user_role == UserRole.ADMIN:
            queryset = queryset.filter(user_role=UserRole.REGULAR)
            user_group_ids = self.request.user.user_user_groups.values_list(
                "user_group__id", flat=True
            )
            queryset = queryset.filter(
                user_user_groups__user_group__id__in=user_group_ids
            )

        return queryset
