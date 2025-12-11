# management/commands/cleanup_expired_transactions.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from transactions.models import Transactions
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up expired transactions based on payment method and status'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate the cleanup without actually deleting',
        )
        parser.add_argument(
            '--log-only',
            action='store_true',
            help='Log expired transactions without deleting',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        dry_run = options['dry_run']
        log_only = options['log_only']
        
        # Define cleanup rules
        cleanup_rules = [
            {
                'payment_method': 'M-Pesa',
                'payment_status': 'Pending',
                'expiry': timedelta(hours=1),
                'description': 'M-Pesa pending for more than 1 hour'
            },
            {
                'payment_method': 'Cheque',
                'payment_status': 'Pending',
                'expiry': timedelta(weeks=1),
                'description': 'Cheque pending for more than 1 week'
            },
            {
                'payment_method': 'Cash',
                'payment_status': 'Pending',
                'expiry': timedelta(days=3),
                'description': 'Cash pending for more than 3 days'
            },
        ]
        
        total_to_delete = 0
        results = []
        
        for rule in cleanup_rules:
            expiry_time = now - rule['expiry']
            
            expired_transactions = Transactions.objects.filter(
                payment_method=rule['payment_method'],
                payment_status=rule['payment_status'],
                donated_at__lt=expiry_time
            )
            
            count = expired_transactions.count()
            
            if count > 0:
                # Log the transactions to be deleted
                for transaction in expired_transactions:
                    logger.info(
                        f'Expired transaction found: ID={transaction.id}, '
                        f'Method={transaction.payment_method}, '
                        f'Status={transaction.payment_status}, '
                        f'Amount={transaction.amount}, '
                        f'Created={transaction.donated_at}'
                    )
                
                # Delete if not dry run or log only
                if not dry_run and not log_only:
                    deleted_count, _ = expired_transactions.delete()
                    action = 'DELETED'
                else:
                    deleted_count = count
                    action = 'FOUND (not deleted - dry run)' if dry_run else 'FOUND (log only)'
                
                results.append({
                    'method': rule['payment_method'],
                    'count': count,
                    'action': action,
                    'description': rule['description']
                })
                total_to_delete += count
        
        # Output results
        if results:
            self.stdout.write(self.style.WARNING(
                f"\n=== Cleanup Summary ===\n"
                f"Total transactions found: {total_to_delete}\n"
            ))
            
            for result in results:
                style = self.style.SUCCESS if 'DELETED' in result['action'] else self.style.WARNING
                self.stdout.write(style(
                    f"{result['method']}: {result['count']} {result['action']} "
                    f"({result['description']})"
                ))
            
            if dry_run or log_only:
                self.stdout.write(self.style.WARNING(
                    "\n⚠️  No transactions were actually deleted (dry run/log only mode)"
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"\n✅ Successfully deleted {total_to_delete} expired transactions"
                ))
        else:
            self.stdout.write(self.style.SUCCESS("No expired transactions found"))