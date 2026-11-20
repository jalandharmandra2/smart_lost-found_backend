from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from found_items.models import FoundItem

User = get_user_model()

class FoundItemsAPITests(TestCase):
    def setUp(self):
        self.finder = User.objects.create_user(username='item_finder_01', password='Password123!', role='ITEM_FINDER')
        self.client = APIClient()

    def test_create_and_list_found_items(self):
        self.client.force_authenticate(user=self.finder)

        img = Image.new('RGB', (100, 100), color=(50, 100, 150))
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_file = SimpleUploadedFile("found_keys.jpg", img_io.getvalue(), content_type="image/jpeg")

        payload = {
            'item_name': 'Set of 3 Keys with Red Keychain',
            'category': 'KEYS',
            'description': 'Found near coffee shop bench',
            'colour': 'Silver and Red',
            'date_found': str(date.today()),
            'found_location': 'University Food Court',
            'latitude': 17.45,
            'longitude': 78.38,
            'current_storage_location': 'Turned in to Desk',
            'image': img_file,
        }

        res = self.client.post('/api/found-items/', payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['item_name'], 'Set of 3 Keys with Red Keychain')

        # Test listing
        list_res = self.client.get('/api/found-items/?category=KEYS')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        results = list_res.data.get('results', list_res.data) if isinstance(list_res.data, dict) else list_res.data
        self.assertTrue(any(i['item_name'] == 'Set of 3 Keys with Red Keychain' for i in results))
