# /home/khalfan/Desktop/JMCDonations/run_donation_closure.py
#!/usr/bin/env python3
"""
Simple script to close expired donations.
Run this with cron every hour.
"""

import os
import sys
import logging
from datetime import datetime

# ==================== CONFIGURATION ====================
PROJECT_PATH = '/home/khalfan/Desktop/JMCDonations'
VENV_PYTHON = '/home/khalfan/Desktop/JMCDonations/venv/bin/python'
LOG_FILE = '/home/khalfan/donation_closure.log'
# =======================================================

# Add project to path
sys.path.append(PROJECT_PATH)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def setup_django():
    """Setup Django environment"""
    try:
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JMCDonations.settings')
        
        # Import Django
        import django
        django.setup()
        
        logger.info("✅ Django setup successful")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure Django is installed in the virtual environment")
        logger.error(f"Virtual environment Python: {VENV_PYTHON}")
        return False
    except Exception as e:
        logger.error(f"❌ Django setup error: {e}")
        return False

def close_expired_donations():
    """Close donations that have passed their end date"""
    logger.info("=" * 60)
    logger.info("START: Checking for expired donations")
    logger.info(f"Time: {datetime.now()}")
    logger.info(f"Python executable: {sys.executable}")
    
    try:
        # Setup Django
        if not setup_django():
            return {"status": "error", "message": "Django setup failed"}
        
        # Now import Django modules
        from django.utils import timezone
        from donations.models import Donations
        
        # Get current time in Django's timezone
        now = timezone.now()
        logger.info(f"System time: {now}")
        
        # 1. Close donations that have passed their end date
        expired_donations = Donations.objects.filter(
            end_date__lt=now,
            status='Active'
        )
        expired_count = expired_donations.update(status='Closed')
        logger.info(f"✅ Closed {expired_count} expired donation(s)")
        
        # 2. Close donations that have reached their target amount
        funded_count = 0
        active_donations = Donations.objects.filter(status='Active')
        for donation in active_donations:
            if donation.check_and_close_if_funded():
                funded_count += 1
                logger.info(f"✅ Closed fully funded donation: {donation.title} (ID: {donation.id})")
        
        logger.info(f"✅ SUCCESS: Closed {expired_count + funded_count} total donation(s)")
        
        # Return summary
        return {
            "status": "success",
            "expired": expired_count,
            "funded": funded_count,
            "total_closed": expired_count + funded_count,
            "timestamp": now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}
    
    finally:
        logger.info("END: Donation closure completed")
        logger.info("=" * 60)

if __name__ == "__main__":
    # Run the function
    result = close_expired_donations()
    
    # Exit with appropriate code
    if result.get("status") == "error":
        sys.exit(1)
    else:
        sys.exit(0)