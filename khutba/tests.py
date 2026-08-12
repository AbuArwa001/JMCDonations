import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from khutba.models import JumaKhutba, DeviceToken
from events.models import Event, EventCategory
import datetime
from unittest.mock import patch
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestNotificationsFlow:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email='admin@test.com',
            username='admin',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a device token
        DeviceToken.objects.create(fcm_token='test_token_123', platform='ios')
        
    @patch('firebase_admin.messaging.send_multicast')
    def test_khutba_notify_on_publish(self, mock_send):
        url = reverse('khutba-list')
        data = {
            'khutba_date': '2023-11-10',
            'khutba_time': '13:30:00',
            'imam_name': 'Sheikh Test',
            'title': 'Test Khutba',
            'published': True
        }
        
        # When creating a new published khutba, auto_notify_khutba signal is triggered
        response = self.client.post(url, data, format='json')
        assert response.status_code == 201
        
        # Check that FCM mock was called
        assert mock_send.called
        
        # Verify the message payload
        args, kwargs = mock_send.call_args
        message = args[0]
        assert 'Test Khutba' in message.notification.title
        assert 'Sheikh Test' in message.notification.body
        assert 'test_token_123' in message.tokens
        
    @patch('firebase_admin.messaging.send_multicast')
    def test_event_notify_on_publish(self, mock_send):
        category = EventCategory.objects.create(name='Lecture', slug='lecture')
        
        url = reverse('event-list')
        data = {
            'title': 'Test Event',
            'category': category.id,
            'story': '<p>Details</p>',
            'event_date': '2023-11-12',
            'start_time': '10:00:00',
            'venue_name': 'Main Hall',
            'published': True
        }
        
        # When creating a new published event, auto_notify_event signal is triggered
        response = self.client.post(url, data, format='json')
        assert response.status_code == 201
        
        # Check that FCM mock was called
        assert mock_send.called
        
        # Verify the message payload
        args, kwargs = mock_send.call_args
        message = args[0]
        assert 'Test Event' in message.notification.title
        assert 'Main Hall' in message.notification.body
        assert 'test_token_123' in message.tokens
