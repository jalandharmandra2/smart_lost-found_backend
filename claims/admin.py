from django.contrib import admin
from .models import ClaimRequest

@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'claimant', 'found_item', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('claim_description', 'claimant__username')
