from django.contrib import admin
from .models import AdminAuditLog

@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin_user', 'action_type', 'target_model', 'target_id', 'timestamp')
    list_filter = ('action_type', 'timestamp')
