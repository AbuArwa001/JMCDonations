# authentication.py
import os
import firebase_admin
from firebase_admin import auth, credentials
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings

User = get_user_model()

# Global flag to track initialization
_firebase_initialized = False

def initialize_firebase():
    global _firebase_initialized
    if not _firebase_initialized:
        try:
            service_account_path = os.path.join(settings.BASE_DIR, 'config', 'jmcdonations.json')
            
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase Admin initialized successfully")
            else:
                print(f"❌ Firebase service account file not found at: {service_account_path}")
                # Try default initialization for development
                firebase_admin.initialize_app()
                print("✅ Firebase Admin initialized with default credentials")
            
            _firebase_initialized = True
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            raise

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        # Skip if no authorization header
        if not auth_header:
            return None

        # Check if it's a Bearer token
        if not auth_header.startswith('Bearer '):
            return None

        id_token = auth_header.split(' ').pop()
        
        if not id_token:
            return None

        # Ensure Firebase is initialized
        try:
            initialize_firebase()
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Firebase not configured: {e}')

        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(id_token)
            
            if not decoded_token:
                return None

            uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            
            if not email:
                raise exceptions.AuthenticationFailed('Firebase token must have an email')

            # Get or create user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create new user
                user = User.objects.create(
                    email=email,
                    username=email,  # Use email as username
                    is_active=True
                )
                print(f"✅ Created new user: {email}")

            # Update Firebase UID if not set
            if not user.firebase_uid:
                user.firebase_uid = uid
                user.save()

            return (user, None)
            
        except auth.InvalidIdTokenError:
            raise exceptions.AuthenticationFailed('Invalid Firebase token')
        except auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed('Firebase token expired')
        except auth.RevokedIdTokenError:
            raise exceptions.AuthenticationFailed('Firebase token revoked')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')