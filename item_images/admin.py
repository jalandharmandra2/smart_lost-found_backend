from django.contrib import admin
from .models import ItemImage

@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'lost_item', 'found_item', 'is_primary', 'uploaded_at')
