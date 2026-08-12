from django.db import models

class DuaCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100, blank=True, help_text="Image or icon key")
    display_order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Dua Categories"
        ordering = ['display_order', 'name']
        
    def __str__(self):
        return self.name

class Dua(models.Model):
    category = models.ForeignKey(DuaCategory, on_delete=models.CASCADE, related_name='duas')
    title = models.CharField(max_length=200)
    arabic_text = models.TextField()
    transliteration = models.TextField(blank=True, null=True)
    translation_en = models.TextField()
    translation_sw = models.TextField(blank=True, null=True)
    source_reference = models.CharField(max_length=200, blank=True, null=True)
    audio_url = models.URLField(blank=True, null=True)
    display_order = models.IntegerField(default=0)
    published = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'display_order', 'title']
        
    def __str__(self):
        return self.title
