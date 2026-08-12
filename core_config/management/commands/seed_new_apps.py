from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from core_config.models import AppFeature
from duas.models import DuaCategory, Dua
from quran.models import Reciter
from prayer_times.models import City, PrayerCalculationSettings
from khutba.models import JumaKhutba
from events.models import EventCategory, Event

class Command(BaseCommand):
    help = 'Seeds new apps with initial data'

    def handle(self, *args, **options):
        # 1. Feature Toggles
        features = ['duas', 'quran', 'prayer_times', 'zakat_calculator', 'khutba', 'events']
        for feat in features:
            AppFeature.objects.update_or_create(name=feat, defaults={'is_active': True})
        self.stdout.write(self.style.SUCCESS('Seeded feature toggles.'))

        # 2. Duas
        categories = ['Morning & Evening', 'Before/After Eating', 'Travel', 'Protection & Distress', 'General']
        for idx, cat_name in enumerate(categories):
            DuaCategory.objects.get_or_create(
                name=cat_name, 
                slug=cat_name.lower().replace(' ', '-').replace('/', '-').replace('&', 'and'), 
                defaults={'display_order': idx + 1}
            )
        self.stdout.write(self.style.SUCCESS('Seeded dua categories.'))

        # 3. Quran Reciters
        reciters = [
            {'name': 'Mishary Rashid Alafasy'},
            {'name': 'Abdul Rahman Al-Sudais'},
            {'name': 'Saad Al Ghamdi'},
        ]
        for reciter in reciters:
            Reciter.objects.get_or_create(name=reciter['name'])
        self.stdout.write(self.style.SUCCESS('Seeded Quran reciters.'))

        # 4. Prayer Times Cities
        cities = [
            {'name': 'Nairobi', 'lat': -1.2921, 'lon': 36.8219},
            {'name': 'Mombasa', 'lat': -4.0435, 'lon': 39.6682},
            {'name': 'Kisumu', 'lat': -0.0917, 'lon': 34.7680},
            {'name': 'Nakuru', 'lat': -0.3031, 'lon': 36.0800},
            {'name': 'Eldoret', 'lat': 0.5143, 'lon': 35.2698},
        ]
        for c in cities:
            City.objects.get_or_create(name=c['name'], defaults={'latitude': c['lat'], 'longitude': c['lon'], 'timezone': 'Africa/Nairobi'})
        
        # Ensure prayer calculation setting exists
        PrayerCalculationSettings.load()
        self.stdout.write(self.style.SUCCESS('Seeded prayer time cities and settings.'))

        # 5. Khutba
        today = datetime.date.today()
        # Find next Friday
        next_friday = today + datetime.timedelta((4 - today.weekday()) % 7)
        khutba, _ = JumaKhutba.objects.get_or_create(
            title='Sample Juma Khutba',
            defaults={
                'khutba_date': next_friday,
                'khutba_time': datetime.time(13, 30),
                'imam_name': 'Sheikh Placeholder',
                'topic_summary': 'This is a sample khutba topic.',
                'published': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Seeded sample Khutba.'))

        # 6. Events
        evt_cat, _ = EventCategory.objects.get_or_create(name='Lecture', slug='lecture')
        Event.objects.get_or_create(
            title='Hajj Preparation Lecture',
            defaults={
                'category': evt_cat,
                'story': '<p>Join us for an important lecture on preparing for Hajj.</p>',
                'event_date': next_friday + datetime.timedelta(days=1),
                'start_time': datetime.time(10, 0),
                'venue_name': 'Jamia Mosque Main Hall',
                'guest_name': 'Sheikh Visitor',
                'published': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Seeded sample Event.'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded all new apps.'))
