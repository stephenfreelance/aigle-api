from rest_framework.permissions import BasePermission

from core.models.user import UserRole


class AdminRolePermission(BasePermission):
    message = "Vous devez être administrateur pour accéder à cette ressource"

    def has_permission(self, request, view):
        if request.user and not request.user.is_anonymous and request.user.user_role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return True

        return False
