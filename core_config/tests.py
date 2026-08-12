import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from core_config.models import AppFeature

@pytest.mark.django_db
class TestFeatureToggles:
    def test_feature_toggle_read(self):
        AppFeature.objects.create(name='khutba', is_active=True)
        AppFeature.objects.create(name='events', is_active=False)
        
        client = APIClient()
        url = reverse('features-list')
        response = client.get(url)
        
        assert response.status_code == 200
        data = response.json()
        
        results = data.get('results', data) if isinstance(data, dict) else data
        assert len(results) >= 2
        
        features = {f['name']: f['is_active'] for f in results}
        assert features.get('khutba') is True
        assert features.get('events') is False
