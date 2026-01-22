from firebase_admin import messaging
import logging

logger = logging.getLogger(__name__)

def send_topic_notification(topic, title, body, data=None):
    """
    Sends a push notification to a specific FCM topic.
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            topic=topic,
            data=data,
        )
        response = messaging.send(message)
        logger.info(f"Successfully sent message to topic {topic}: {response}")
        return response
    except Exception as e:
        logger.error(f"Error sending message to topic {topic}: {e}")
        return None

def send_new_donation_notification(donation_title, donation_id):
    """
    Convenience function to notify users about a new donation drive.
    """
    title = "New Donation Drive! 📢"
    body = f"A new donation drive '{donation_title}' has been started. Tap to contribute."
    data = {
        "click_action": "FLUTTER_NOTIFICATION_CLICK",
        "type": "new_donation",
        "donation_id": str(donation_id),
    }
    # We send to the 'all_users' topic which Flutter app should subscribe to
    return send_topic_notification("all_users", title, body, data)
