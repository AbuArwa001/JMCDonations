# sync_firebase_to_django.py
import os
import django
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from django.contrib.auth.hashers import make_password

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JMCDonations.settings')
django.setup()

from users.models import Users, Roles

def sync_users():
    # Initialize Firebase (same as your set_admin_claims.py)
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate('config/jmcdonations.json')
        firebase_admin.initialize_app(cred)
    
    # Get all Firebase users
    firebase_users = auth.list_users().iterate_all()
    
    for firebase_user in firebase_users:
        email = firebase_user.email
        firebase_uid = firebase_user.uid
        
        if not email:
            continue
        
        # Determine role based on email
        if email == 'admin@example.com':
            role_name = 'admin'
            is_admin = True
            is_staff = True
        elif email == 'accountant@example.com':
            role_name = 'Accountant'
            is_admin = True
            is_staff = True
        elif email == 'finance@example.com':
            role_name = 'Finance Officer'
            is_admin = True
            is_staff = True
        else:
            role_name = 'User'
            is_admin = False
            is_staff = False
        
        # Get or create role
        role, _ = Roles.objects.get_or_create(role_name=role_name)
        
        # Check if user exists
        try:
            user = Users.objects.get(email=email)
            # Update existing user
            user.firebase_uid = firebase_uid
            user.role = role
            user.is_admin = is_admin
            user.is_staff = is_staff
            user.save()
            print(f"✅ Updated: {email}")
        except Users.DoesNotExist:
            # Create new user
            username = email.split('@')[0]
            Users.objects.create(
                email=email,
                username=username,
                firebase_uid=firebase_uid,
                full_name=firebase_user.display_name or username,
                role=role,
                is_admin=is_admin,
                is_staff=is_staff,
                is_active=True,
                # Set a password (won't be used for Firebase auth)
                password=make_password(firebase_uid)
            )
            print(f"✅ Created: {email}")

if __name__ == '__main__':
    sync_users()
    print("\n✅ Sync complete!")