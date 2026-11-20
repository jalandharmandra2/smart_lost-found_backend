from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from lost_items.models import LostItem

User = get_user_model()

class LostItemsAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='item_owner', password='Password123!', role='GENERAL_USER')
        self.other_user = User.objects.create_user(username='other_person', password='Password123!', role='GENERAL_USER')
        self.client = APIClient()

    def test_create_lost_item_with_image(self):
        self.client.force_authenticate(user=self.user)

        # Create dummy image in memory
        img = Image.new('RGB', (100, 100), color=(10, 20, 30))
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_file = SimpleUploadedFile("test_wallet.jpg", img_io.getvalue(), content_type="image/jpeg")

        payload = {
            'item_name': 'Lost Leather Wallet',
            'category': 'WALLETS_PURSE',
            'description': 'Dark leather wallet with cash and cards',
            'colour': 'Dark Brown',
            'date_lost': str(date.today()),
            'location': 'Central Bus Terminus',
            'latitude': 17.445,
            'longitude': 78.375,
            'secret_identifying_details': 'Driver license #DL-99128 inside flap',
            'image': img_file,
        }

        res = self.client.post('/api/lost-items/', payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['item_name'], 'Lost Leather Wallet')
        self.assertTrue(len(res.data['images']) >= 1)

        # Check embedding generation on the uploaded image
        created_item = LostItem.objects.get(id=res.data['id'])
        self.assertTrue(created_item.images.first().embedding is not None)
        self.assertEqual(len(created_item.images.first().embedding), 512)

    def test_redaction_for_non_owner(self):
        item = LostItem.objects.create(
            user=self.user,
            item_name="Secret Watch",
            category="JEWELRY_WATCHES",
            description="Gold watch",
            colour="Gold",
            date_lost=date.today(),
            location="City Mall",
            secret_identifying_details="Serial #999-SECRET-999"
        )

        # Authenticated as other user
        self.client.force_authenticate(user=self.other_user)
        res = self.client.get(f'/api/lost-items/{item.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn("Serial #999-SECRET-999", res.data['secret_identifying_details'])
        self.assertIn("REDACTED", res.data['secret_identifying_details'])

        # Authenticated as owner
        self.client.force_authenticate(user=self.user)
        owner_res = self.client.get(f'/api/lost-items/{item.id}/')
        self.assertIn("Serial #999-SECRET-999", owner_res.data['secret_identifying_details'])
