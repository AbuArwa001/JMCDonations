
import firebase_admin
from firebase_admin import auth
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ').pop()
        if not token:
            return None

        try:
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            
            # Check for admin claim in the token
            is_firebase_admin = decoded_token.get('admin', False)
            
            # Improved lookup logic to prevent UNIQUE constraint errors
            try:
                user = User.objects.get(email=email)
                if not getattr(user, 'firebase_uid', None):
                    user.firebase_uid = uid
                    user.save()
                    print(f"✅ Linked existing user {email} to firebase_uid in auth backend")
            except User.DoesNotExist:
                user = User.objects.create(
                    email=email,
                    firebase_uid=uid,
                    username=email.split('@')[0], 
                    is_active=True,
                    is_admin=is_firebase_admin
                )
                print(f"✅ Created new user {email} in auth backend")

            # Sync admin status if it changed in Firebase
            if user.is_admin != is_firebase_admin:
                user.is_admin = is_firebase_admin
                user.save()
            
            return (user, None)
        except Exception as e:
            logger.error(f"Firebase authentication failed: {e}")
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')

""" # authentication.py
import os
import firebase_admin
from firebase_admin import auth, credentials
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions
from JMCDonations import settings
import json

User = get_user_model()

# Global flag to track initialization
_firebase_initialized = False

def initialize_firebase():
    global _firebase_initialized
    if not _firebase_initialized:
        try:
            # 1. Try initializing from Environment Variable (Production)
            service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
            if service_account_json:
                try:
                    service_account_info = json.loads(service_account_json)
                    cred = credentials.Certificate(service_account_info)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase Admin initialized from Environment Variable")
                    _firebase_initialized = True
                    return
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
            
            # 2. Try initializing from File (Local Development)
            service_account_path = os.path.join(settings.BASE_DIR, 'config', 'jmcdonations.json')
            
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase Admin initialized from File")
            else:
                print(f"⚠️ Firebase service account file not found at: {service_account_path}")
                print("ℹ️ Trying to initialize with default credentials...")
                # Try default initialization (e.g. for GCloud environment)
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
            # Provide more detailed error
            error_msg = f'Firebase initialization failed: {str(e)}. '
            error_msg += 'Check if FIREBASE_SERVICE_ACCOUNT_JSON is set or service account file exists.'
            raise exceptions.AuthenticationFailed(error_msg)

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
                # Create new user with username (required by Django)
                # Generate a username from email or use uid
                username = email.split('@')[0] if '@' in email else uid
                
                # Make sure username is unique
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=None  # No password for Firebase users
                )
                print(f"✅ Created new user: {email} with username: {username}")

            # Optional: Store Firebase UID if you have the field
            # Check if the field exists before trying to save it
            if hasattr(user, 'firebase_uid'):
                if not user.firebase_uid:
                    user.firebase_uid = uid
                    user.save()
            else:
                # If you don't have the field, you can store it in a separate model
                # or just skip it
                pass

            return (user, None)
            
        except auth.InvalidIdTokenError:
            raise exceptions.AuthenticationFailed('Invalid Firebase token')
        except auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed('Firebase token expired')
        except auth.RevokedIdTokenError:
            raise exceptions.AuthenticationFailed('Firebase token revoked')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}') """