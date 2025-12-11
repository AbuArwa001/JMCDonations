# donations/tasks.py
from celery import shared_task 
from django.utils import timezone
from django.core.management import call_command
from .models import Donations
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def close_expired_donations_task(self):
    """
    Celery task to close expired donations
    """
    try:
        logger.info("🔄 Starting close_expired_donations_task")
        
        now = timezone.now()
        expired_donations = Donations.objects.filter(
            end_date__lt=now,
            status='Active'
        )
        
        count = expired_donations.count()
        
        if count == 0:
            logger.info("✅ No expired donations found")
            return {
                "status": "success", 
                "closed": 0, 
                "message": "No expired donations found"
            }
        
        # Log what we're about to close
        donation_info = []
        for donation in expired_donations:
            donation_info.append({
                'id': str(donation.id),
                'title': donation.title,
                'end_date': donation.end_date.isoformat()
            })
            logger.info(f"📋 Will close: {donation.title} (ID: {donation.id})")
        
        # Close them
        updated_count = expired_donations.update(status='Closed')
        
        logger.info(f"✅ Successfully closed {updated_count} donations")
        return {
            "status": "success",
            "closed": updated_count,
            "donations": donation_info,
            "timestamp": now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error in close_expired_donations_task: {str(e)}")
        # Retry the task after 5 minutes if it fails
        raise self.retry(exc=e)

@shared_task
def close_expired_donations_management_command():
    """
    Alternative: Run the management command as a Celery task
    """
    try:
        from django.core.management import call_command
        logger.info("🔄 Running close_expired_donations management command via Celery")
        call_command('close_expired_donations')
        return {"status": "success", "message": "Command executed"}
    except Exception as e:
        logger.error(f"❌ Error running management command: {str(e)}")
        return {"status": "error", "message": str(e)}

@shared_task
def test_celery_connection():
    """
    Test task to verify Celery is working
    """
    logger.info("✅ Celery is working!")
    return {
        "status": "success",
        "message": "Celery task executed successfully",
        "timestamp": timezone.now().isoformat()
    }
# @shared_task(bind=True, max_retries=3)
# def close_expired_donations_task(self):
#     """
#     Celery task to close expired donations
#     """
#     try:
#         logger.info("Starting close_expired_donations_task")
        
#         now = timezone.now()
#         expired_donations = Donations.objects.filter(
#             end_date__lt=now,
#             status='Active'
#         )
        
#         count = expired_donations.count()
        
#         if count == 0:
#             logger.info("No expired donations found")
#             return {"status": "success", "closed": 0, "message": "No expired donations"}
        
#         # Log what we're about to close
#         donation_titles = [d.title for d in expired_donations]
#         logger.info(f"Found {count} expired donations: {donation_titles}")
        
#         # Close them
#         updated_count = expired_donations.update(status='Closed')
        
#         # Send notifications if needed
#         for donation in expired_donations:
#             logger.info(
#                 f'Donation auto-closed via Celery: ID={donation.id}, '
#                 f'Title="{donation.title}", End Date={donation.end_date}'
#             )
        
#         logger.info(f"Successfully closed {updated_count} donations")
#         return {
#             "status": "success",
#             "closed": updated_count,
#             "donations": donation_titles
#         }
        
#     except Exception as e:
#         logger.error(f"Error in close_expired_donations_task: {str(e)}")
#         # Retry the task after 5 minutes if it fails
#         raise self.retry(exc=e, countdown=300)

# @shared_task
# def check_and_notify_expiring_donations():
#     """
#     Check for donations expiring soon and send notifications
#     """
#     from django.utils import timezone
#     from datetime import timedelta
    
#     warning_threshold = timezone.now() + timedelta(hours=24)  # 24 hours warning
    
#     expiring_soon = Donations.objects.filter(
#         end_date__lte=warning_threshold,
#         end_date__gt=timezone.now(),
#         status='Active'
#     )
    
#     # Here you could add email notifications, etc.
#     for donation in expiring_soon:
#         logger.info(f"Donation expiring soon: {donation.title} (ends: {donation.end_date})")
    
#     return {"expiring_soon": expiring_soon.count()}

# @shared_task
# def donation_health_check():
#     """
#     Periodic health check for donation system
#     """
#     from django.utils import timezone
    
#     stats = {
#         "total_donations": Donations.objects.count(),
#         "active_donations": Donations.objects.filter(status='Active').count(),
#         "expired_active": Donations.objects.filter(
#             end_date__lt=timezone.now(),
#             status='Active'
#         ).count(),
#         "check_time": timezone.now().isoformat(),
#     }
    
#     logger.info(f"Donation health check: {stats}")
#     return stats
