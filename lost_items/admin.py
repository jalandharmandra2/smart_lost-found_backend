from django.contrib import admin
from .models import LostItem

@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_name', 'category', 'colour', 'date_lost', 'location', 'user', 'status', 'created_at')
    list_filter = ('category', 'status', 'is_active', 'date_lost')
    search_fields = ('item_name', 'description', 'location', 'colour')
