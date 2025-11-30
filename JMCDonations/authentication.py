import os
import firebase_admin
from firebase_admin import auth, credentials
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings

User = get_user_model()

def initialize_firebase():
    if not firebase_admin._apps:
        # Check if we have a service account path in settings or env
        service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH')
        
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback for development/testing if no creds provided (might fail strict auth)
            # Or assume default credentials (Google Cloud)
            try:
                firebase_admin.initialize_app()
            except Exception as e:
                print(f"Warning: Firebase Admin not initialized: {e}")

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        id_token = auth_header.split(' ').pop()
        
        # Ensure Firebase is initialized
        initialize_firebase()

        try:
            decoded_token = auth.verify_id_token(id_token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Invalid Firebase token: {e}')

        if not decoded_token:
            return None

        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        
        if not email:
             raise exceptions.AuthenticationFailed('Firebase token must have an email')

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email, # Use email as username
                'is_active': True
            }
        )

        return (user, None)
