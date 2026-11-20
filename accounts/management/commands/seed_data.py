from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from datetime import date, timedelta
from io import BytesIO
from PIL import Image, ImageDraw
from lost_items.models import LostItem
from found_items.models import FoundItem
from item_images.models import ItemImage
from locations.models import LocationPoint
from ai_matching.services import extract_clip_embedding, find_and_record_matches_for_lost_item, find_and_record_matches_for_found_item
from notifications.models import Notification

User = get_user_model()

def create_synthetic_image(color_rgb, shape_type="rectangle", text="Item"):
    """Create a sample image in memory using PIL for test data."""
    img = Image.new("RGB", (256, 256), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)

    if shape_type == "rectangle":
        draw.rectangle([40, 60, 216, 196], fill=color_rgb, outline=(30, 30, 30), width=3)
    elif shape_type == "circle":
        draw.ellipse([50, 50, 206, 206], fill=color_rgb, outline=(30, 30, 30), width=3)
    elif shape_type == "backpack":
        draw.rounded_rectangle([60, 40, 196, 220], radius=30, fill=color_rgb, outline=(20, 20, 20), width=4)
        draw.rectangle([80, 110, 176, 190], fill=(20, 20, 20))

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = "Seed database with demonstration users, locations, lost & found items, and AI matches."

    def handle(self, *args, **options):
        self.stdout.write("Starting database seed...")

        # 1. Create Users
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@smartlostfound.local",
                "first_name": "Platform",
                "last_name": "Admin",
                "role": User.Role.ADMINISTRATOR,
                "is_staff": True,
                "is_superuser": True,
                "is_verified": True
            }
        )
        admin_user.set_password("AdminPassword123!")
        admin_user.save()

        user1, _ = User.objects.get_or_create(
            username="rahul_sharma",
            defaults={
                "email": "rahul.sharma@example.com",
                "first_name": "Rahul",
                "last_name": "Sharma",
                "role": User.Role.GENERAL_USER,
                "phone_number": "+91 98765 43210",
                "address": "Hyderabad, Telangana",
                "is_verified": True
            }
        )
        user1.set_password("UserPassword123!")
        user1.save()

        user2, _ = User.objects.get_or_create(
            username="priya_patel",
            defaults={
                "email": "priya.patel@example.com",
                "first_name": "Priya",
                "last_name": "Patel",
                "role": User.Role.ITEM_FINDER,
                "phone_number": "+91 91234 56789",
                "address": "Banjara Hills, Hyderabad",
                "is_verified": True
            }
        )
        user2.set_password("FinderPassword123!")
        user2.save()

        self.stdout.write(self.style.SUCCESS("Demo users created."))

        # 2. Locations
        locations_data = [
            {"name": "HITEC City Metro Station", "city": "Hyderabad", "latitude": 17.4475, "longitude": 78.3762},
            {"name": "Central University Library", "city": "Hyderabad", "latitude": 17.4568, "longitude": 78.3312},
            {"name": "Inorbit Mall Food Court", "city": "Hyderabad", "latitude": 17.4348, "longitude": 78.3867},
            {"name": "Rajiv Gandhi Intl Airport T1", "city": "Hyderabad", "latitude": 17.2403, "longitude": 78.4294},
            {"name": "Secunderabad Railway Station", "city": "Hyderabad", "latitude": 17.4339, "longitude": 78.5042},
        ]
        for loc in locations_data:
            LocationPoint.objects.get_or_create(name=loc["name"], city=loc["city"], defaults=loc)

        self.stdout.write(self.style.SUCCESS("Geographical location points created."))

        # 3. Create Sample Lost Items
        today = date.today()
        lost1, _ = LostItem.objects.get_or_create(
            item_name="Black Leather Tommy Hilfiger Wallet",
            defaults={
                "user": user1,
                "category": "WALLETS_PURSE",
                "description": "Black bi-fold leather wallet containing student ID card, Metro smart card, and some cash.",
                "colour": "Black",
                "brand_or_maker": "Tommy Hilfiger",
                "date_lost": today - timedelta(days=2),
                "location": "HITEC City Metro Station, Hyderabad",
                "latitude": 17.4475,
                "longitude": 78.3762,
                "contact_preference": "IN_APP",
                "secret_identifying_details": "Driving License #DL07-2022001928, small tear on inner card slot.",
                "reward_amount": 500.00,
                "status": "ACTIVE"
            }
        )
        if not lost1.images.exists():
            img_file = create_synthetic_image((30, 30, 30), "rectangle", "Wallet")
            item_img = ItemImage.objects.create(lost_item=lost1, is_primary=True)
            item_img.image.save("lost_black_wallet.jpg", img_file, save=True)
            try:
                item_img.embedding = extract_clip_embedding(item_img.image.path)
                item_img.save(update_fields=["embedding"])
            except Exception:
                pass

        lost2, _ = LostItem.objects.get_or_create(
            item_name="Blue Wildcraft Backpack with Laptop",
            defaults={
                "user": user1,
                "category": "BAGS_LUGGAGE",
                "description": "Navy blue Wildcraft 30L waterproof backpack with silver zippers and water bottle pocket.",
                "colour": "Navy Blue",
                "brand_or_maker": "Wildcraft",
                "date_lost": today - timedelta(days=1),
                "location": "Inorbit Mall Food Court, Hyderabad",
                "latitude": 17.4348,
                "longitude": 78.3867,
                "contact_preference": "IN_APP",
                "secret_identifying_details": "Grey Dell Inspiron 15 inside main compartment, serial ending in 4921.",
                "reward_amount": 1000.00,
                "status": "ACTIVE"
            }
        )
        if not lost2.images.exists():
            img_file = create_synthetic_image((25, 45, 120), "backpack", "Backpack")
            item_img = ItemImage.objects.create(lost_item=lost2, is_primary=True)
            item_img.image.save("lost_blue_backpack.jpg", img_file, save=True)
            try:
                item_img.embedding = extract_clip_embedding(item_img.image.path)
                item_img.save(update_fields=["embedding"])
            except Exception:
                pass

        # 4. Create Sample Found Items
        found1, _ = FoundItem.objects.get_or_create(
            item_name="Found Men's Black Leather Wallet",
            defaults={
                "user": user2,
                "category": "WALLETS_PURSE",
                "description": "Found a black leather wallet near the ticket counter gate. Kept safely.",
                "colour": "Black",
                "date_found": today - timedelta(days=1),
                "found_location": "HITEC City Metro Gate 2, Hyderabad",
                "latitude": 17.4478,
                "longitude": 78.3765,
                "current_storage_location": "With Finder Priya Patel (Metro Commuter)",
                "status": "ACTIVE"
            }
        )
        if not found1.images.exists():
            img_file = create_synthetic_image((35, 35, 35), "rectangle", "Wallet Found")
            item_img = ItemImage.objects.create(found_item=found1, is_primary=True)
            item_img.image.save("found_black_wallet.jpg", img_file, save=True)
            try:
                item_img.embedding = extract_clip_embedding(item_img.image.path)
                item_img.save(update_fields=["embedding"])
            except Exception:
                pass

        found2, _ = FoundItem.objects.get_or_create(
            item_name="Navy Blue College Bag / Backpack",
            defaults={
                "user": user2,
                "category": "BAGS_LUGGAGE",
                "description": "Navy blue backpack left on a table in the food court 3rd floor.",
                "colour": "Blue",
                "date_found": today - timedelta(days=1),
                "found_location": "Inorbit Mall 3rd Floor Food Court, Hyderabad",
                "latitude": 17.4350,
                "longitude": 78.3870,
                "current_storage_location": "Mall Customer Service Desk",
                "status": "ACTIVE"
            }
        )
        if not found2.images.exists():
            img_file = create_synthetic_image((30, 50, 130), "backpack", "Backpack Found")
            item_img = ItemImage.objects.create(found_item=found2, is_primary=True)
            item_img.image.save("found_blue_backpack.jpg", img_file, save=True)
            try:
                item_img.embedding = extract_clip_embedding(item_img.image.path)
                item_img.save(update_fields=["embedding"])
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS("Lost and Found sample items created with synthetic images."))

        # 5. Run AI Matching Inference
        self.stdout.write("Computing AI similarity scores across sample records...")
        find_and_record_matches_for_lost_item(lost1)
        find_and_record_matches_for_lost_item(lost2)

        self.stdout.write(self.style.SUCCESS("AI similarity matching completed and persisted to MySQL."))
