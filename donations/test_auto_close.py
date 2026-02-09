from django.test import TestCase
from django.utils import timezone
from donations.models import Donations
from transactions.models import Transactions
from categories.models import Categories
from users.models import Users
from run_donation_closure import close_expired_donations
import decimal

class DonationAutoCloseTest(TestCase):
    def setUp(self):
        self.user = Users.objects.create_user(username="testuser", password="testpass")
        self.category = Categories.objects.create(name="Education")
        self.donation = Donations.objects.create(
            title="Test Donation",
            description="Test Description",
            paybill_number="123456",
            account_name="TestAccount",
            target_amount=decimal.Decimal("1000.00"),
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30),
            status="Active",
            category=self.category,
            created_by=self.user
        )

    def test_signal_closes_donation_when_funded(self):
        """Test that a completed transaction reaching the target completes the donation"""
        self.assertEqual(self.donation.status, "Active")
        
        # Create a completed transaction for the full amount
        Transactions.objects.create(
            donation=self.donation,
            amount=decimal.Decimal("1000.00"),
            payment_status="Completed",
            payment_method="M-Pesa"
        )
        
        # Refresh from DB
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, "Completed")

    def test_auto_close_when_expired(self):
        """Test that donation closes when remaining days < 0"""
        # Set end_date to yesterday
        self.donation.end_date = timezone.now() - timezone.timedelta(days=1)
        self.donation.save()
        
        # Check logic
        self.assertTrue(self.donation.is_expired())
        self.assertTrue(self.donation.remaining_days < 0)
        
        # Re-save to trigger status update or call method
        self.donation.status = "Active"
        self.donation.auto_update_status()
        
        self.assertEqual(self.donation.status, "Closed")

    def test_script_closes_funded_and_expired_donations(self):
        """Test that run_donation_closure.py handles both cases"""
        # 1. Funded case
        donation_funded = Donations.objects.create(
            title="Funded Donation",
            target_amount=decimal.Decimal("100.00"),
            end_date=timezone.now() + timezone.timedelta(days=10),
            category=self.category,
            created_by=self.user,
            status="Active"
        )
        Transactions.objects.create(
            donation=donation_funded,
            amount=decimal.Decimal("100.00"),
            payment_status="Completed",
            payment_method="M-Pesa"
        )
        # Manually reset to Active to test script
        donation_funded.status = "Active"
        donation_funded.save()

        # 2. Expired case
        donation_expired = Donations.objects.create(
            title="Expired Donation",
            target_amount=decimal.Decimal("1000.00"),
            end_date=timezone.now() - timezone.timedelta(days=2),
            category=self.category,
            created_by=self.user,
            status="Active"
        )

        # Run the script logic
        result = close_expired_donations()
        
        self.assertEqual(result["total_closed"], 2)
        
        donation_funded.refresh_from_db()
        donation_expired.refresh_from_db()
        
        self.assertEqual(donation_funded.status, "Completed")
        self.assertEqual(donation_expired.status, "Closed")
