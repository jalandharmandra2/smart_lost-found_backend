from django.db import models

class MatchRecord(models.Model):
    MATCH_LABELS = [
        ('HIGH', 'High similarity'),
        ('MEDIUM', 'Medium similarity'),
        ('LOW', 'Low similarity'),
    ]

    STATUS_CHOICES = [
        ('NEW', 'New Match'),
        ('VIEWED', 'Viewed by User'),
        ('CLAIM_INITIATED', 'Claim Initiated'),
        ('CONFIRMED', 'Confirmed Match'),
        ('DISMISSED', 'Dismissed as Not Match'),
    ]

    lost_item = models.ForeignKey(
        'lost_items.LostItem',
        on_delete=models.CASCADE,
        related_name='matches'
    )
    found_item = models.ForeignKey(
        'found_items.FoundItem',
        on_delete=models.CASCADE,
        related_name='matches'
    )
    
    # Detailed factor scores (0.0 to 1.0)
    image_similarity = models.FloatField(default=0.0, help_text="Cosine similarity between CLIP image embeddings (weight: 60%)")
    category_similarity = models.FloatField(default=0.0, help_text="Category match score (weight: 15%)")
    color_similarity = models.FloatField(default=0.0, help_text="Colour semantic similarity (weight: 10%)")
    text_similarity = models.FloatField(default=0.0, help_text="Title and description similarity (weight: 10%)")
    distance_km = models.FloatField(null=True, blank=True, help_text="Geographical distance in kilometers")
    location_proximity_score = models.FloatField(default=0.0, help_text="Proximity score based on distance (weight: 5%)")
    
    # Final composite score (0.0 to 1.0)
    total_score = models.FloatField(default=0.0, db_index=True)
    match_label = models.CharField(max_length=20, choices=MATCH_LABELS, default='LOW')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='NEW')
    
    response_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_score', '-created_at']
        constraints = [
            models.UniqueConstraint(fields=['lost_item', 'found_item'], name='unique_lost_found_match')
        ]

    def __str__(self):
        return f"Match: Lost #{self.lost_item_id} <-> Found #{self.found_item_id} ({self.total_score:.1%}, {self.match_label})"
