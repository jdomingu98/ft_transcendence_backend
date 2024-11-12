from rest_framework.permissions import BasePermission

ACTIONS_THAT_DO_NOT_REQUIRE_AUTH = [
    "create",
    "login",
    "otp",
    "password_reset",
    "refresh",
    "change_password",
    "oauth",
    "verify_account",
]


class UserPermissions(BasePermission):
    def has_permission(self, request, view):
        if view.action in ACTIONS_THAT_DO_NOT_REQUIRE_AUTH:
            return True
        return request.user.is_authenticated
