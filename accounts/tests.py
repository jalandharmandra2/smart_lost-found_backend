from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AccountsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.profile_url = '/api/auth/profile/'

    def test_user_registration(self):
        payload = {
            'username': 'test_user_001',
            'email': 'test001@example.com',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
            'role': 'GENERAL_USER'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['username'], 'test_user_001')

    def test_user_login_and_profile(self):
        user = User.objects.create_user(
            username='login_tester',
            email='tester@example.com',
            password='TestPassword123!'
        )
        login_res = self.client.post(self.login_url, {
            'username': 'login_tester',
            'password': 'TestPassword123!'
        }, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        token = login_res.data['tokens']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        profile_res = self.client.get(self.profile_url)
        self.assertEqual(profile_res.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_res.data['username'], 'login_tester')
