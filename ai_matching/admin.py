from django.contrib import admin
from .models import MatchRecord

@admin.register(MatchRecord)
class MatchRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'lost_item', 'found_item', 'total_score', 'match_label', 'status', 'created_at')
    list_filter = ('match_label', 'status')
