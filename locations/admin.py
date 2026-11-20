from django.contrib import admin
from .models import LocationPoint

@admin.register(LocationPoint)
class LocationPointAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'latitude', 'longitude')
    search_fields = ('name', 'city')
