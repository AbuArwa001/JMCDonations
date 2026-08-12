import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "JMCDonations.settings")
django.setup()

from prayer_times.models import City

kenyan_cities = [
    {"name": "Nairobi", "latitude": -1.286389, "longitude": 36.817223},
    {"name": "Mombasa", "latitude": -4.043477, "longitude": 39.668206},
    {"name": "Kisumu", "latitude": -0.091702, "longitude": 34.767956},
    {"name": "Nakuru", "latitude": -0.303099, "longitude": 36.080025},
    {"name": "Eldoret", "latitude": 0.514277, "longitude": 35.269779},
    {"name": "Malindi", "latitude": -3.219186, "longitude": 40.116890},
    {"name": "Garissa", "latitude": -0.453229, "longitude": 39.646099},
    {"name": "Machakos", "latitude": -1.517684, "longitude": 37.263412},
    {"name": "Thika", "latitude": -1.03326, "longitude": 37.06933},
    {"name": "Lamu", "latitude": -2.269559, "longitude": 40.900642}
]

City.objects.all().delete()

for c_data in kenyan_cities:
    City.objects.create(
        name=c_data["name"],
        latitude=c_data["latitude"],
        longitude=c_data["longitude"],
        timezone="Africa/Nairobi",
        is_active=True
    )
print(f"Added {len(kenyan_cities)} Kenyan cities successfully!")
