# sync_firebase_users.py (updated)
import os
import django
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from django.contrib.auth.hashers import make_password
from django.db import models

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JMCDonations.settings')
django.setup()

from users.models import Users, Roles

# Initialize Firebase Admin SDK (if not already initialized)
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate('config/jmcdonations.json')
    firebase_admin.initialize_app(cred)

def sync_firebase_users():
    """Sync Firebase users with Django database"""
    
    try:
        # Get all Firebase users
        firebase_users = auth.list_users().iterate_all()
        
        user_count = 0
        for firebase_user in firebase_users:
            email = firebase_user.email
            firebase_uid = firebase_user.uid
            display_name = firebase_user.display_name or ""
            
            if not email:
                print(f"Skipping user without email: {firebase_uid}")
                continue
            
            # Map emails to roles
            role_map = {
                'admin@example.com': 'admin',
                'finance@example.com': 'Finance Officer',
                'accountant@example.com': 'Accountant',
                'john.doe@example.com': 'User',
                'jane.smith@example.com': 'User', 
                'alice.johnson@example.com': 'User',
                'bob.brown@example.com': 'User',
                'anonymous@donor.com': 'User' 
            }
            
            # Determine role
            role_name = role_map.get(email, 'User')
            role, _ = Roles.objects.get_or_create(role_name=role_name)
            
            # Generate username from email
            username = email.split('@')[0]
            
            # Check if user exists by firebase_uid or email
            user = Users.objects.filter(
                models.Q(firebase_uid=firebase_uid) | models.Q(email=email)
            ).first()
            
            if user:
                # Update existing user
                user.firebase_uid = firebase_uid
                user.username = username
                user.full_name = display_name or user.full_name or username
                user.role = role
                user.is_active = True
                user.is_admin = (role_name == 'admin')
                user.is_staff = (role_name in ['admin', 'Accountant', 'Finance Officer'])
                user.save()
                print(f"✅ Updated: {email} ({role_name})")
            else:
                # Create new user
                user = Users.objects.create(
                    email=email,
                    username=username,
                    firebase_uid=firebase_uid,
                    full_name=display_name or username,
                    role=role,
                    is_active=True,
                    is_admin=(role_name == 'admin'),
                    is_staff=(role_name in ['admin', 'Accountant', 'Finance Officer']),
                    password=make_password(firebase_uid)
                )
                print(f"✅ Created: {email} ({role_name})")
            
            user_count += 1
        
        print(f"\n✅ Successfully synced {user_count} users")
        
    except Exception as e:
        print(f"❌ Error syncing users: {str(e)}")

if __name__ == "__main__":
    sync_firebase_users()