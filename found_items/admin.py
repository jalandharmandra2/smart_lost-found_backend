from django.contrib import admin
from .models import FoundItem

@admin.register(FoundItem)
class FoundItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_name', 'category', 'colour', 'date_found', 'found_location', 'user', 'status', 'created_at')
    list_filter = ('category', 'status', 'is_active', 'date_found')
    search_fields = ('item_name', 'description', 'found_location', 'colour')
