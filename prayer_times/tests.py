import pytest
import datetime
from django.urls import reverse
from prayer_times.models import City, PrayerCalculationSettings, PrayerTimeOverride
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestPrayerTimes:
    def setup_method(self):
        self.client = APIClient()
        self.city = City.objects.create(
            name="Nairobi",
            latitude=-1.2921,
            longitude=36.8219,
            timezone="Africa/Nairobi"
        )
        PrayerCalculationSettings.objects.create(
            calculation_method='MUSLIM_WORLD_LEAGUE'
        )

    def test_prayer_time_calculation(self):
        url = reverse('prayer-times-calc')
        response = self.client.get(url, {'city': self.city.id, 'date': '2023-10-10'})
        
        assert response.status_code == 200
        data = response.json()
        assert 'fajr' in data
        assert 'dhuhr' in data
        assert 'maghrib' in data

    def test_prayer_time_override(self):
        override_time = datetime.time(5, 30)
        PrayerTimeOverride.objects.create(
            city=self.city,
            date=datetime.date(2023, 10, 10),
            prayer_name='fajr',
            overridden_time=override_time
        )
        
        url = reverse('prayer-times-calc')
        response = self.client.get(url, {'city': self.city.id, 'date': '2023-10-10'})
        
        assert response.status_code == 200
        data = response.json()
        assert data['fajr'] == '05:30:00'
