from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import City, PrayerCalculationSettings, PrayerTimeOverride
from .serializers import CitySerializer, PrayerTimeOverrideSerializer, PrayerCalculationSettingsSerializer
import datetime
from adhan import adhan
from adhan.methods import ISNA, MUSLIM_WORLD_LEAGUE, EGYPT, MAKKAH, KARACHI, TEHRAN, SHIA

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
            'UMM_AL_QURA': MAKKAH,
            'GULF': MAKKAH,
            'KARACHI': KARACHI,
            'TEHRAN': TEHRAN,
            'SHIA': SHIA,
            'OTHER': MUSLIM_WORLD_LEAGUE,
        }
        
        method_params = methods_map.get(method_str, MUSLIM_WORLD_LEAGUE).copy()
        method_params['asr_multiplier'] = 1
        
        import pytz
        tz = pytz.timezone(city.timezone)
        dt = datetime.datetime.combine(date_obj, datetime.time.min)
        offset_seconds = tz.utcoffset(dt).total_seconds()
        offset_hours = offset_seconds / 3600.0
        
        pt = adhan(
            day=date_obj,
            location=(city.latitude, city.longitude),
            parameters=method_params,
            timezone_offset=offset_hours
        )
        
        # Get times and format them
        def format_time(t):
            if not t: return None
            return t.strftime('%H:%M:%S')
            
        result = {
            'fajr': format_time(pt.get('fajr')),
            'sunrise': format_time(pt.get('shuruq')),
            'dhuhr': format_time(pt.get('zuhr')),
            'asr': format_time(pt.get('asr')),
            'maghrib': format_time(pt.get('maghrib')),
            'isha': format_time(pt.get('isha')),
        }
        
        # Apply overrides
        overrides = PrayerTimeOverride.objects.filter(city=city, date=date_obj)
        for override in overrides:
            name = override.prayer_name.lower()
            if name in result:
                result[name] = override.overridden_time.strftime('%H:%M:%S')
                
        return Response(result)

class PrayerTimeOverrideViewSet(viewsets.ModelViewSet):
    queryset = PrayerTimeOverride.objects.all()
    serializer_class = PrayerTimeOverrideSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class PrayerCalculationSettingsAPIView(views.APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]
        
    def get(self, request, *args, **kwargs):
        settings = PrayerCalculationSettings.load()
        serializer = PrayerCalculationSettingsSerializer(settings)
        return Response(serializer.data)
        
    def put(self, request, *args, **kwargs):
        settings = PrayerCalculationSettings.load()
        serializer = PrayerCalculationSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
