from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import City, PrayerCalculationSettings, PrayerTimeOverride
from .serializers import CitySerializer, PrayerTimeOverrideSerializer
import datetime
from adhan import adhan
from adhan.methods import ISNA, MUSLIM_WORLD_LEAGUE, EGYPT, UMM_AL_QURA, GULF, MOONSIGHTING_COMMITTEE, KUWAIT, QATAR, SINGAPORE, TEHRAN, TURKEY, OTHER

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class PrayerTimeAPIView(views.APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        city_id = request.query_params.get('city')
        date_str = request.query_params.get('date')
        
        if not city_id or not date_str:
            return Response({"error": "city and date parameters are required"}, status=400)
            
        city = get_object_or_404(City, pk=city_id)
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
            
        settings = PrayerCalculationSettings.load()
        method_str = settings.calculation_method
        
        methods_map = {
            'MUSLIM_WORLD_LEAGUE': MUSLIM_WORLD_LEAGUE,
            'ISLAMIC_SOCIETY_OF_NORTH_AMERICA': ISNA,
            'NORTH_AMERICA': ISNA,
            'EGYPTIAN': EGYPT,
            'UMM_AL_QURA': UMM_AL_QURA,
            'GULF': GULF,
            'MOONSIGHTING_COMMITTEE': MOONSIGHTING_COMMITTEE,
            'KUWAIT': KUWAIT,
            'QATAR': QATAR,
            'SINGAPORE': SINGAPORE,
            'TEHRAN': TEHRAN,
            'TURKEY': TURKEY,
            'OTHER': OTHER,
        }
        
        method_params = methods_map.get(method_str, MUSLIM_WORLD_LEAGUE)
        
        coordinates = adhan.Coordinates(city.latitude, city.longitude)
        
        # Get prayer times
        pt = adhan.PrayerTimes(coordinates, date_obj, method_params)
        
        # Calculate times based on timezone (simplification here, ideally we'd use pytz with the city.timezone)
        # the adhan package returns datetime objects in UTC, we can convert it to the local timezone.
        # But wait, python adhan package returns time in UTC or local?
        # Actually, python's adhan package by default computes time based on timezone offset.
        
        import pytz
        tz = pytz.timezone(city.timezone)
        
        # Get times and format them
        def format_time(t):
            if not t: return None
            # Convert UTC datetime to the city timezone
            t_local = t.astimezone(tz)
            return t_local.strftime('%H:%M:%S')
            
        result = {
            'fajr': format_time(pt.fajr),
            'sunrise': format_time(pt.sunrise),
            'dhuhr': format_time(pt.dhuhr),
            'asr': format_time(pt.asr),
            'maghrib': format_time(pt.maghrib),
            'isha': format_time(pt.isha),
        }
        
        # Apply overrides
        overrides = PrayerTimeOverride.objects.filter(city=city, date=date_obj)
        for override in overrides:
            name = override.prayer_name.lower()
            if name in result:
                result[name] = override.overridden_time.strftime('%H:%M:%S')
                
        return Response(result)
