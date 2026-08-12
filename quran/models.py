from django.db import models

class Reciter(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='quran/reciters/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class SurahAudio(models.Model):
    surah_number = models.IntegerField(help_text="1 to 114")
    reciter = models.ForeignKey(Reciter, on_delete=models.CASCADE, related_name='surah_audios')
    audio_url = models.URLField()
    duration_seconds = models.IntegerField(blank=True, null=True)
    
    class Meta:
        unique_together = ('surah_number', 'reciter')
        ordering = ['surah_number', 'reciter__name']
        
    def __str__(self):
        return f"Surah {self.surah_number} - {self.reciter.name}"
