# authentication/backends.py
import firebase_admin
from firebase_admin import auth, credentials
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from rest_framework import authentication
from rest_framework import exceptions
import jwt
from django.conf import settings

User = get_user_model()

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            # Extract the token from "Bearer <token>"
            id_token = auth_header.split(' ').pop()
            
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            
            # Get or create the user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'firebase_uid': uid,
                }
            )
            
            # Update Firebase UID if not set
            if not user.firebase_uid:
                user.firebase_uid = uid
                user.save()
            
            return (user, None)
            
        except ValueError:
            raise exceptions.AuthenticationFailed('Invalid Authorization header')
        except auth.InvalidIdTokenError:
            raise exceptions.AuthenticationFailed('Invalid Firebase token')
        except auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed('Firebase token expired')
        except auth.RevokedIdTokenError:
            raise exceptions.AuthenticationFailed('Firebase token revoked')
        except auth.CertificateFetchError:
            raise exceptions.AuthenticationFailed('Error fetching certificates')
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))