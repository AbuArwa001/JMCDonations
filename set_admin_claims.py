# set_admin_claims.py
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials

# Initialize Firebase Admin (you'll need to download serviceAccountKey.json)
# Download from: Firebase Console → Project Settings → Service Accounts
cred = credentials.Certificate('config/jmcdonations.json')
firebase_admin.initialize_app(cred)

def set_admin_claims():
    # Define admin users and their roles
    admin_users = {
        'admin@example.com': {'admin': True, 'role': 'super_admin'},
        'accountant@example.com': {'admin': True, 'role': 'accountant'},
        'finance@example.com': {'admin': True, 'role': 'finance_officer'}
    }
    
    for email, claims in admin_users.items():
        try:
            # Get user by email
            user = auth.get_user_by_email(email)
            
            # Set custom claims
            auth.set_custom_user_claims(user.uid, claims)
            
            print(f"✅ Set admin claims for: {email}")
            print(f"   UID: {user.uid}")
            print(f"   Claims: {claims}")
            
        except Exception as e:
            print(f"❌ Error with {email}: {e}")

if __name__ == '__main__':
    set_admin_claims()