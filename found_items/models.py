from django.db import models
from django.conf import settings

class FoundItem(models.Model):
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
        ('ACTIVE', 'Active / Found'),
        ('CLAIM_PENDING', 'Ownership Claim Pending'),
        ('RECOVERED', 'Returned to True Owner'),
        ('CLOSED', 'Closed / Turned into Authority'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='found_items'
    )
    item_name = models.CharField(max_length=200, db_index=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    description = models.TextField()
    colour = models.CharField(max_length=50, db_index=True)
    date_found = models.DateField(db_index=True)
    found_location = models.CharField(max_length=255, db_index=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Safe custody details
    current_storage_location = models.CharField(
        max_length=255,
        default='With Finder',
        help_text="Current custody location (e.g. Finder Custody, Security Desk, Lost Property Office)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[Found #{self.id}] {self.item_name} ({self.get_category_display()})"
