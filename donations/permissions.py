from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user
    
class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    Assumes the User model has an `is_admin` attribute.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin
    
class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow authenticated users to create/edit,
    but allow read-only access to unauthenticated users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

class IsAuthenticated(permissions.BasePermission):
    """
    Custom permission to only allow authenticated users to access the view.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
class AllowAny(permissions.BasePermission):
    """
    Custom permission to allow any user (authenticated or not) to access the view.
    """

    def has_permission(self, request, view):
        return True