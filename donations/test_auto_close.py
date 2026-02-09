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

    def test_signal_closes_donation(self):
        """Test that a completed transaction reaching the target closes the donation"""
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

    def test_script_closes_funded_donation(self):
        """Test that run_donation_closure.py closes fully funded donations"""
        # Create a completed transaction (without signal if possible, or just check script)
        # We'll create it and if signal already closed it, we'll reopen it to test script
        Transactions.objects.create(
            donation=self.donation,
            amount=decimal.Decimal("1000.00"),
            payment_status="Completed",
            payment_method="M-Pesa"
        )
        
        # Manually set back to Active and disable signals for a moment if needed
        # but let's just test if the script handles it.
        self.donation.status = "Active"
        self.donation.save()
        
        self.assertEqual(self.donation.status, "Active")
        
        # Run the script logic
        result = close_expired_donations()
        
        self.assertEqual(result["funded"], 1)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, "Completed")
