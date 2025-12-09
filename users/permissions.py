from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    Assumes the User model has an `is_admin` attribute.
    """

    def has_permission(self, request, view):
        print("Checking admin permission for user:", request.user)
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsAdminOrSelf(BasePermission):
    """
    Allows access only to admins or the user accessing his own data.
    """

    def has_object_permission(self, request, view, obj):
        # Admin can access anything
        if request.user and request.user.is_staff:
            return True
        
        # Normal user can only access their own account
        return obj.pk == request.user.pk