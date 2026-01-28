import firebase_admin
from firebase_admin import auth
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class FirebaseDRFAuthentication(authentication.BaseAuthentication):
    """
    Authentication backend for Django REST Framework.
    Returns (User, None) tuple.
    API: GET /api/v1/... (with Bearer token)
    """
    def authenticate(self, request):
        return self._authenticate_credentials(request)

    def _authenticate_credentials(self, request, token=None):
        # 1. Initialize logic
        if not token:
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ').pop()
            
            # Fallback for Web UI
            if not token and hasattr(request, 'data'):
                if isinstance(request.data, dict):
                    token = request.data.get('token')

        if not token:
            return None
        
        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            
            # Use 'admin' claim if you have set custom claims in Firebase
            is_firebase_admin = decoded_token.get('admin', False)
            
            # Get or create the user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'firebase_uid': uid,
                    'is_staff': is_firebase_admin,    
                    'is_superuser': is_firebase_admin 
                }
            )
            
            # Sync user details
            should_save = False
            if not user.firebase_uid:
                user.firebase_uid = uid
                should_save = True

            if user.is_staff != is_firebase_admin:
                user.is_staff = is_firebase_admin
                user.is_superuser = is_firebase_admin
                should_save = True
            
            if should_save:
                user.save()

            return (user, None)
            
        except auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed('Firebase token expired')
        except auth.InvalidIdTokenError:
            raise exceptions.AuthenticationFailed('Invalid Firebase token')
        except Exception as e:
            logger.error(f"Firebase auth error: {e}")
            raise exceptions.AuthenticationFailed(str(e))

class FirebaseDjangoAuthentication:
    """
    Authentication backend for Django Admin / Login sessions.
    Returns User object (not tuple).
    API: /admin/ login
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Attempt to get token from request if present (e.g. customized login)
        # Or simple pass-through if bridging from view
        # This wrapper re-uses the logic above but returns just user
        
        # Check if we have an explicit token passed directly (from bridge view)
        token = kwargs.get('token')
        
        # Or try to extract from request like DRF does
        drf_auth = FirebaseDRFAuthentication()
        try:
            result = drf_auth._authenticate_credentials(request, token=token)
            if result:
                return result[0] # Return just the User
        except Exception:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
