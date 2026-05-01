from django.contrib import admin
from .models import CommunityContent

@admin.register(CommunityContent)
class CommunityContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'is_published', 'scheduled_for')
    list_filter = ('content_type', 'is_published')
    search_fields = ('title', 'author_or_sheikh')
