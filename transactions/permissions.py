from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    """
    Custom permission to only allow authenticated users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated