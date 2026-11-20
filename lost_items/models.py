from django.db import models
from django.conf import settings

class LostItem(models.Model):
    CATEGORY_CHOICES = [
        ('ELECTRONICS', 'Electronics & Gadgets'),
        ('WALLETS_PURSE', 'Wallets & Purses'),
        ('BAGS_LUGGAGE', 'Bags & Luggage'),
        ('JEWELRY_WATCHES', 'Jewelry & Watches'),
        ('KEYS', 'Keys & Keychain'),
        ('DOCUMENTS_IDS', 'Documents, Cards & IDs'),
        ('CLOTHING_ACCESSORIES', 'Clothing & Accessories'),
        ('PETS', 'Pets & Animals'),
        ('VEHICLES', 'Bicycles & Vehicles'),
        ('BOOKS_STATIONERY', 'Books & Stationery'),
        ('OTHER', 'Other Belongings'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active / Lost'),
        ('MATCHED', 'Potential Match Found'),
        ('RECOVERED', 'Recovered'),
        ('CLOSED', 'Closed / Cancelled'),
    ]

    CONTACT_PREFERENCES = [
        ('IN_APP', 'In-App Messaging Only (Safest)'),
        ('EMAIL', 'Platform Email Forwarding'),
        ('PHONE', 'Direct Phone Call'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lost_items'
    )
    item_name = models.CharField(max_length=200, db_index=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    description = models.TextField()
    colour = models.CharField(max_length=50, db_index=True)
    brand_or_maker = models.CharField(max_length=100, blank=True)
    date_lost = models.DateField(db_index=True)
    location = models.CharField(max_length=255, db_index=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Private verification information (never exposed in public API)
    secret_identifying_details = models.TextField(
        blank=True,
        help_text="Confidential marks, serial numbers, passwords/lock patterns known only to the genuine owner."
    )
    contact_preference = models.CharField(
        max_length=20,
        choices=CONTACT_PREFERENCES,
        default='IN_APP'
    )
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[Lost #{self.id}] {self.item_name} ({self.get_category_display()})"
