from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from uuid import uuid4

from categories.models import Categories
from donations.models import Donations, SavedDonations
from transactions.models import Transactions
from users.models import Roles


class Command(BaseCommand):
    help = 'Seed the database with demo data: roles, users, categories, donations, transactions.'

    def add_arguments(self, parser):
        parser.add_argument('--skip-transactions', action='store_true', help='Do not create sample transactions')

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write('Seeding demo data...')

        # Roles
        admin_role, _ = Roles.objects.get_or_create(role_name='admin')
        donor_role, _ = Roles.objects.get_or_create(role_name='donor')

        # Users (idempotent)
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'full_name': 'Admin User',
                'is_staff': True,
                'is_superuser': True,
                'is_admin': True,
            }
        )
        if created:
            admin_user.set_password('adminpass')
            admin_user.role = admin_role
            admin_user.save()
            self.stdout.write('  created admin user: admin@example.com / adminpass')
        else:
            self.stdout.write('  admin user already exists')

        donor_user, created = User.objects.get_or_create(
            email='donor@example.com',
            defaults={
                'username': 'donor',
                'full_name': 'Demo Donor',
                'is_staff': False,
            }
        )
        if created:
            donor_user.set_password('donorpass')
            donor_user.role = donor_role
            donor_user.save()
            self.stdout.write('  created donor user: donor@example.com / donorpass')
        else:
            self.stdout.write('  donor user already exists')

        # Categories
        cats = ['General', 'Education', 'Health', 'Emergency']
        cat_objs = {}
        for name in cats:
            obj, _ = Categories.objects.get_or_create(category_name=name)
            cat_objs[name] = obj
        self.stdout.write(f'  ensured categories: {", ".join(cat_objs.keys())}')

        # Donations (idempotent by title)
        now = timezone.now()
        donations_to_create = [
            {
                'title': 'School Supplies Fund',
                'description': 'Buy school supplies for children in need',
                'paybill_number': '123456',
                'account_name': 'SchoolFund',
                'category': cat_objs['Education'],
                'target_amount': '5000.00',
                'start_date': now,
                'end_date': now + timezone.timedelta(days=90),
                'status': 'Active',
                'created_by': admin_user,
            },
            {
                'title': 'Health Camp Support',
                'description': 'Support our free health camps',
                'paybill_number': '123457',
                'account_name': 'HealthCamp',
                'category': cat_objs['Health'],
                'target_amount': '10000.00',
                'start_date': now,
                'end_date': now + timezone.timedelta(days=60),
                'status': 'Active',
                'created_by': admin_user,
            },
        ]

        donation_objs = {}
        for d in donations_to_create:
            obj, created = Donations.objects.get_or_create(title=d['title'], defaults=d)
            donation_objs[obj.title] = obj
            if created:
                self.stdout.write(f"  created donation: {obj.title}")
            else:
                self.stdout.write(f"  donation already exists: {obj.title}")

        # Optionally create transactions
        if not options.get('skip_transactions'):
            # Create a couple of sample transactions
            tx1, created = Transactions.objects.get_or_create(
                transaction_reference=f"TX-{uuid4()}",
                defaults={
                    'donation': donation_objs['School Supplies Fund'],
                    'user': donor_user,
                    'recorded_by_admin_id': admin_user,
                    'amount': '50.00',
                    'payment_method': 'M-Pesa',
                    'payment_status': 'Completed',
                    'completed_at': now,
                }
            )
            if created:
                self.stdout.write(f"  created transaction: {tx1.transaction_reference}")
            else:
                self.stdout.write('  sample transaction already exists')

            tx2, created = Transactions.objects.get_or_create(
                transaction_reference=f"TX-{uuid4()}",
                defaults={
                    'donation': donation_objs['Health Camp Support'],
                    'user': donor_user,
                    'recorded_by_admin_id': admin_user,
                    'amount': '100.00',
                    'payment_method': 'Card',
                    'payment_status': 'Completed',
                    'completed_at': now,
                }
            )
            if created:
                self.stdout.write(f"  created transaction: {tx2.transaction_reference}")
        else:
            self.stdout.write('  skipped transactions as requested')

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
