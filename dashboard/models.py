from django.db import models
from django.conf import settings

class AdminAuditLog(models.Model):
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_audit_logs'
    )
    action_type = models.CharField(max_length=100, db_index=True)
    target_model = models.CharField(max_length=100)
    target_id = models.IntegerField()
    details = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.admin_user.username} -> {self.action_type} on {self.target_model}#{self.target_id}"
