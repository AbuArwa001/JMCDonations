from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
import random
from django.contrib.auth import get_user_model
from categories.models import Categories
from donations.models import Donations
from transactions.models import Transactions

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds historical donations and transactions from July 2026 to Dec 2026'

    def handle(self, *args, **options):
        # 1. Get or create a category
        category, _ = Categories.objects.get_or_create(category_name="Historical Data", color="#4CAF50")
        
        # 2. Get a user to be creator
        creator = User.objects.filter(is_superuser=True).first()
        if not creator:
            creator = User.objects.first()
            
        if not creator:
            self.stdout.write(self.style.ERROR('No users found in database to attach as creator.'))
            return
            
        # 3. Create a few donations across the months
        start_date = datetime.date(2026, 7, 1)
        end_date = datetime.date(2026, 12, 31)
        delta = end_date - start_date
        
        for i in range(15): # 15 dummy campaigns
            random_days = random.randint(0, delta.days)
            campaign_start = start_date + datetime.timedelta(days=random_days)
            campaign_end = campaign_start + datetime.timedelta(days=random.randint(15, 60))
            
            status = "Closed" if campaign_end < datetime.date.today() else "Active"
            
            donation = Donations.objects.create(
                title=f"Historical Campaign {i+1}",
                description="This is a historical campaign generated for analytics purposes.",
                paybill_number="123456",
                account_name="JMC Account",
                category=category,
                target_amount=random.randint(50000, 500000),
                start_date=timezone.make_aware(datetime.datetime.combine(campaign_start, datetime.time.min)),
                end_date=timezone.make_aware(datetime.datetime.combine(campaign_end, datetime.time.max)),
                status=status,
                created_by=creator
            )
            # Update created_at manually as auto_now_add overrides it on create
            Donations.objects.filter(id=donation.id).update(
                created_at=timezone.make_aware(datetime.datetime.combine(campaign_start, datetime.time.min))
            )
            
            # 4. Add transactions to this campaign
            num_transactions = random.randint(10, 40)
            for j in range(num_transactions):
                tx_days = random.randint(0, (campaign_end - campaign_start).days)
                tx_date = campaign_start + datetime.timedelta(days=tx_days)
                if tx_date > datetime.date.today():
                    continue # don't add future transactions
                    
                tx_time = timezone.make_aware(datetime.datetime.combine(tx_date, datetime.time(random.randint(8, 20), random.randint(0, 59))))
                
                tx = Transactions.objects.create(
                    donation=donation,
                    user=creator,
                    amount=random.randint(100, 10000),
                    payment_method=random.choice(["M-Pesa", "Card", "Cash"]),
                    payment_status="Completed",
                    transaction_reference=f"HIST-{donation.id.hex[:4]}-{j}-{random.randint(1000,9999)}",
                    mpesa_receipt=f"REC{random.randint(100000,999999)}"
                )
                Transactions.objects.filter(id=tx.id).update(donated_at=tx_time, completed_at=tx_time)
                
        self.stdout.write(self.style.SUCCESS('Successfully seeded historical data (July-Dec 2026).'))
