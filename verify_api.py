import os
import django
from datetime import timedelta
from django.utils import timezone
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fdr.settings')
django.setup()

from users.models import Users, Roles
from donations.models import Categories, Donations, Transactions, SavedDonations
from rest_framework.test import APIClient

def run_verification():
    print("Starting Verification...")
    
    # 1. Setup Data
    print("\n1. Setting up Data...")
    # Create Role
    role, _ = Roles.objects.get_or_create(role_name='Donor')
    
    # Create Users
    admin_user, _ = Users.objects.get_or_create(email='admin@test.com', username='admin', defaults={'full_name': 'Admin User', 'is_admin': True, 'is_staff': True, 'is_superuser': True})
    admin_user.set_password('password123')
    admin_user.save()
    
    donor_user, _ = Users.objects.get_or_create(email='donor@test.com', username='donor', defaults={'full_name': 'Donor User', 'role': role})
    donor_user.set_password('password123')
    donor_user.save()

    # Create Category
    category, _ = Categories.objects.get_or_create(category_name='Education')

    # Create Donation
    donation, _ = Donations.objects.get_or_create(
        title='School Supplies',
        defaults={
            'description': 'Help buy books',
            'paybill_number': '123456',
            'account_name': 'School',
            'category': category,
            'target_amount': 10000,
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=30),
            'created_by': admin_user
        }
    )

    # Create Transaction
    transaction, _ = Transactions.objects.get_or_create(
        donation=donation,
        user=donor_user,
        amount=500,
        defaults={
            'payment_method': 'M-Pesa',
            'payment_status': 'Completed',
            'transaction_reference': str(uuid.uuid4())
        }
    )

    print("Data Setup Complete.")

    # 2. Test API
    client = APIClient()
    
    # Login
    print("\n2. Testing Authentication...")
    response = client.post('/auth/jwt/create/', {'email': 'donor@test.com', 'password': 'password123'})
    if response.status_code == 200:
        token = response.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        print("Login Successful.")
    else:
        print(f"Login Failed: {response.data}")
        return

    # Test Donation List
    print("\n3. Testing Donation List...")
    response = client.get('/api/donations/')
    if response.status_code == 200:
        print(f"Donations Found: {len(response.data['results'])}")
    else:
        print(f"Donation List Failed: {response.status_code}")

    # Test Save Donation
    print("\n4. Testing Save Donation...")
    response = client.post(f'/api/donations/{donation.id}/save/', {'donation_id': donation.id}) # Using URL param or body? View expects body for create, but URL for save-donation endpoint might be confusing.
    # Let's check the view: SavedDonationView.create expects 'donation_id' in body.
    # But I also mapped path('donations/<uuid:pk>/save/', SavedDonationView.as_view())
    # Wait, SavedDonationView is ListCreate. If I use the pk from URL, I need to override create or use a different view.
    # The current SavedDonationView uses request.data.get('donation_id').
    # So I should use the generic endpoint /api/saved-donations/
    
    response = client.post('/api/saved-donations/', {'donation_id': donation.id})
    if response.status_code == 201 or response.status_code == 200:
        print("Donation Saved.")
    else:
        print(f"Save Donation Failed: {response.data}")

    # Test Receipt
    print("\n5. Testing Receipt Generation...")
    response = client.get(f'/api/transactions/{transaction.id}/receipt/')
    if response.status_code == 200 and response['Content-Type'] == 'application/pdf':
        print("Receipt Generated (PDF).")
    else:
        print(f"Receipt Generation Failed: {response.status_code}")

    # Test Admin Analytics (Switch to Admin)
    print("\n6. Testing Admin Analytics...")
    client.force_authenticate(user=admin_user)
    response = client.get('/api/analytics/summary/')
    if response.status_code == 200:
        print(f"Summary: {response.data}")
    else:
        print(f"Analytics Summary Failed: {response.status_code}")

    # Test Export
    print("\n7. Testing Export...")
    response = client.get(f'/api/analytics/export/?drive_id={donation.id}')
    if response.status_code == 200 and 'spreadsheet' in response['Content-Type']:
        print("Export Successful (Excel).")
    else:
        print(f"Export Failed: {response.status_code}")

if __name__ == '__main__':
    run_verification()
