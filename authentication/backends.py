import firebase_admin
from firebase_admin import auth
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # 1. Initialize token as None to prevent UnboundLocalError
        token = None
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        # 2. Try to get token from Header
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ').pop()
        
        # 3. Fallback: Try to get token from Request Body (useful for DRF Web UI)
        if not token and hasattr(request, 'data'):
            token = request.data.get('token')

        # 4. If no token found anywhere, move to the next backend
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
                    'is_staff': is_firebase_admin,    # Needed for /admin/
                    'is_superuser': is_firebase_admin # Needed for /admin/
                }
            )
            
            # Sync UID if it's a legacy user without one
            if not user.firebase_uid:
                user.firebase_uid = uid
                user.save()

            if user.is_staff != is_firebase_admin:
                user.is_staff = is_firebase_admin
                user.is_superuser = is_firebase_admin
                user.save()
            return (user, None)
            
        except auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed('Firebase token expired')
        except auth.InvalidIdTokenError:
            raise exceptions.AuthenticationFailed('Invalid Firebase token')
        except Exception as e:
            logger.error(f"Firebase auth error: {e}")
            raise exceptions.AuthenticationFailed(str(e))

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None