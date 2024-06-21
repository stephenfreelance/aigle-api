from common.views.base import BaseViewSetMixin
from django_filters import FilterSet, CharFilter


from core.models.user_group import UserGroup
from core.serializers.user_group import UserGroupInputSerializer, UserGroupSerializer
from core.utils.permissions import AdminRoleModifyActionPermission


class UserGroupFilter(FilterSet):
    q = CharFilter(method="search")

    class Meta:
        model = UserGroup
        fields = ["q"]

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)


class UserGroupViewSet(BaseViewSetMixin[UserGroup]):
    filterset_class = UserGroupFilter
    permission_classes = [AdminRoleModifyActionPermission]

    def get_serializer_class(self):
        if self.action in ["create", "partial_update", "update"]:
            return UserGroupInputSerializer

        return UserGroupSerializer

    def get_queryset(self):
        queryset = UserGroup.objects.order_by("name")
        return queryset.distinct()
