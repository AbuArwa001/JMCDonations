# management/commands/close_expired_donations.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from donations.models import Donations
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Close donations whose end_date has passed'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be closed without actually updating',
        )
        parser.add_argument(
            '--only-active',
            action='store_true',
            help='Only close Active donations (skip already closed)',
        )
        parser.add_argument(
            '--donation-ids',
            nargs='+',
            type=str,
            help='Specific donation IDs to check and close',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        dry_run = options['dry_run']
        only_active = options['only_active']
        specific_ids = options.get('donation_ids')
        
        # Build the base queryset
        if specific_ids:
            queryset = Donations.objects.filter(id__in=specific_ids)
            self.stdout.write(f"Checking specific donations: {specific_ids}")
        else:
            queryset = Donations.objects.all()
        
        # Filter by end_date and status if needed
        expired_donations = queryset.filter(end_date__lt=now)
        
        if only_active:
            expired_donations = expired_donations.filter(status='Active')
        
        # Count before update
        count = expired_donations.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No expired donations found."))
            return
        
        # Display what will be closed
        self.stdout.write(self.style.WARNING(
            f"\n=== Found {count} expired donation(s) ==="
        ))
        
        for donation in expired_donations:
            self.stdout.write(
                f"• {donation.title} (ID: {donation.id}) - "
                f"Ended: {donation.end_date}, Current Status: {donation.status}"
            )
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\n⚠️  Dry run mode: No donations were actually closed."
            ))
            return
        
        # Actually update the donations
        updated_count = expired_donations.update(status='Closed')
        
        # Log the action
        for donation in expired_donations:
            logger.info(
                f'Donation auto-closed: ID={donation.id}, '
                f'Title="{donation.title}", '
                f'End Date={donation.end_date}, '
                f'Previous Status={donation.status}'
            )
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Successfully closed {updated_count} donation(s)"
        ))
        
        # Optional: Send notifications or perform other actions
        self._post_closure_actions(expired_donations)
    
    def _post_closure_actions(self, donations):
        """Optional: Add post-closure actions like sending notifications"""
        # You can add email notifications, webhook calls, etc. here
        pass