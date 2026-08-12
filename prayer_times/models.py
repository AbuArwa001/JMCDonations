from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timezone = models.CharField(max_length=50, default="Africa/Nairobi")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Cities"
        
    def __str__(self):
        return self.name

class PrayerCalculationSettings(models.Model):
    METHOD_CHOICES = (
        ('MUSLIM_WORLD_LEAGUE', 'Muslim World League'),
        ('ISLAMIC_SOCIETY_OF_NORTH_AMERICA', 'ISLAMIC_SOCIETY_OF_NORTH_AMERICA'),
        ('EGYPTIAN', 'Egyptian General Authority of Survey'),
        ('UMM_AL_QURA', 'Umm Al-Qura University, Makkah'),
        ('GULF', 'Gulf Region'),
        ('MOONSIGHTING_COMMITTEE', 'Moonsighting Committee Worldwide'),
        ('NORTH_AMERICA', 'North America (ISNA)'),
        ('KUWAIT', 'Kuwait'),
        ('QATAR', 'Qatar'),
        ('SINGAPORE', 'Majlis Ugama Islam Singapura, Singapore'),
        ('TEHRAN', 'Institute of Geophysics, University of Tehran'),
        ('TURKEY', 'Diyanet İşleri Başkanlığı, Turkey'),
        ('OTHER', 'Other'),
    )
    
    calculation_method = models.CharField(max_length=100, choices=METHOD_CHOICES, default='MUSLIM_WORLD_LEAGUE')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Prayer Calculation Settings"
        
    def __str__(self):
        return f"Calculation Method: {self.get_calculation_method_display()}"
        
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class PrayerTimeOverride(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='overrides')
    date = models.DateField()
    prayer_name = models.CharField(max_length=50) # Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha
    overridden_time = models.TimeField()
    reason = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        unique_together = ('city', 'date', 'prayer_name')
        
    def __str__(self):
        return f"{self.city.name} - {self.date} - {self.prayer_name} override"
