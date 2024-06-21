from typing import List, Optional
from rest_framework.permissions import BasePermission

from core.models.user import UserRole
from rest_framework.request import Request
from rest_framework.views import APIView


class AdminRolePermission(BasePermission):
    message = "Vous devez être administrateur pour accéder à cette ressource"

    def __init__(self, restricted_actions: Optional[List[str]] = None):
        self.restricted_actions = restricted_actions or []

    def has_permission(self, request: Request, view: APIView):
        if (
            request.user
            and not request.user.is_anonymous
            and request.user.user_role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
        ):
            return True

        return False


# base actions: list, retrieve, create, update, partial_update, destroy
def get_admin_role_permission(
    restricted_actions: Optional[List[str]] = None,
) -> AdminRolePermission:
    class CustomAdminRolePermission(AdminRolePermission):
        def __init__(self):
            super().__init__(restricted_actions)

    return CustomAdminRolePermission


BASE_ACTIONS = ["list", "retrieve", "create", "update", "partial_update", "destroy"]
READ_ACTIONS = ["list", "retrieve"]
MODIFY_ACTIONS = list(set(BASE_ACTIONS) - set(READ_ACTIONS))

AdminRoleModifyActionPermission = get_admin_role_permission(MODIFY_ACTIONS)
