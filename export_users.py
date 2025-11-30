# A simple script you can run manually or as a Django management command

import csv
import django
from django.contrib.auth import get_user_model
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JMCDonations.settings')
django.setup() # Uncomment if running as a standalone script
from django.contrib.auth import get_user_model
User = get_user_model()

def export_users_to_csv():
    users = User.objects.all()
    file_path = 'django_users_export.csv'
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # We need email and optional full_name
        writer.writerow(['email', 'displayName', 'passwordHash', 'passwordSalt'])
        
        for user in users:
            # If you are storing local passwords in a usable format (unlikely with Django defaults), you can add them.
            # Otherwise, these users will need to use "Forgot Password" with Firebase after import.
            writer.writerow([user.email, user.full_name, '', '']) 
    print(f"Exported {users.count()} users to {file_path}")

# Run this function once:
# export_users_to_csv()
if __name__ == "__main__":
    export_users_to_csv()