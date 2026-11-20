from django.db import models
from django.conf import settings

class ClaimRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Initial Review'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Claim Approved (Ownership Verified)'),
        ('REJECTED', 'Claim Rejected'),
        ('DISPUTED', 'Disputed Claim'),
        ('COMPLETED', 'Completed (Item Handed Over)'),
    ]

    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_claims'
    )
    found_item = models.ForeignKey(
        'found_items.FoundItem',
        on_delete=models.CASCADE,
        related_name='claims'
    )
    lost_item = models.ForeignKey(
        'lost_items.LostItem',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='associated_claims'
    )
    
    # Ownership verification answers (kept confidential)
    claim_description = models.TextField(
        help_text="Claimant's detailed explanation of circumstances, purchase details, or recognizable traits."
    )
    secret_identifying_answers = models.TextField(
        help_text="Private verification answers - serial numbers, inner compartment contents, scratches, or PINs. Never exposed publicly."
    )
    supporting_document = models.FileField(
        upload_to='claims/proofs/%Y/%m/',
        null=True,
        blank=True,
        help_text="Optional receipt, warranty card, IMEI proof, or purchase invoice."
    )
    
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    
    # Workflow feedback
    finder_response = models.TextField(
        blank=True,
        help_text="Response or verification comments from the item finder."
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes by platform administrators."
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='claims_reviewed'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Claim #{self.id} on FoundItem #{self.found_item_id} by {self.claimant.username} [{self.status}]"
