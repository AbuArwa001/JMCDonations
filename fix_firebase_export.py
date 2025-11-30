# fixed_scrypt_export.py
import csv
import base64
import os
import django
import sys
import binascii

sys.path.append('/home/khalfan/Documents/JMCDonations')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JMCDonations.settings')
django.setup()

from users.models import Users

def create_fixed_scrypt_export():
    with open('fixed_scrypt_export.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['uid', 'email', 'emailVerified', 'passwordHash', 'salt', 'displayName', 'photoUrl', 'disabled']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for user in Users.objects.all():
            try:
                if user.password and user.password.startswith('pbkdf2_sha256$'):
                    parts = user.password.split('$')
                    
                    if len(parts) >= 4:
                        salt = parts[2]
                        django_hash = parts[3]
                        
                        print(f"Processing: {user.email}")
                        print(f"Salt: {salt}")
                        print(f"Hash: {django_hash[:50]}...")
                        
                        # Django stores the hash as base64, but we need to handle it properly
                        # The hash in Django is already base64 encoded, so we use it as-is
                        password_hash_b64 = django_hash
                        
                        # For salt, we need to base64 encode it since it's stored as plain text in Django
                        salt_b64 = base64.b64encode(salt.encode('utf-8')).decode('utf-8')
                        
                        writer.writerow({
                            'uid': str(user.id),
                            'email': user.email,
                            'emailVerified': 'true',
                            'passwordHash': password_hash_b64,
                            'salt': salt_b64,
                            'displayName': user.full_name or user.username,
                            'photoUrl': '',
                            'disabled': 'false'
                        })
                        print(f"✓ Exported: {user.email}")
                        
            except Exception as e:
                print(f"✗ Error with {user.email}: {e}")
                import traceback
                traceback.print_exc()

if __name__ == '__main__':
    create_fixed_scrypt_export()
    print("\n✅ Fixed SCRYPT export completed: fixed_scrypt_export.csv")