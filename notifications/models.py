from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('MATCH_FOUND', 'Potential Match Identified'),
        ('CLAIM_SUBMITTED', 'New Ownership Claim Submitted'),
        ('CLAIM_ACCEPTED', 'Ownership Claim Accepted'),
        ('CLAIM_REJECTED', 'Ownership Claim Rejected'),
        ('CLAIM_DISPUTED', 'Ownership Claim Disputed'),
        ('ITEM_RECOVERED', 'Item Marked as Recovered'),
        ('REPORT_STATUS', 'Report Status Updated'),
        ('SYSTEM', 'Platform Announcement'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        default='SYSTEM',
        db_index=True
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    action_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.recipient.username}: {self.title} ({'Read' if self.is_read else 'Unread'})"
