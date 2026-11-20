from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class DashboardAdminAPITests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='super_admin',
            password='AdminPassword123!',
            role='ADMINISTRATOR',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='standard_user',
            password='UserPassword123!',
            role='GENERAL_USER'
        )
        self.client = APIClient()

    def test_admin_dashboard_stats_permission(self):
        # Non-admin user receives 403 Forbidden
        self.client.force_authenticate(user=self.regular_user)
        denied_res = self.client.get('/api/dashboard/stats/')
        self.assertEqual(denied_res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin user receives 200 OK and metrics
        self.client.force_authenticate(user=self.admin_user)
        stats_res = self.client.get('/api/dashboard/stats/')
        self.assertEqual(stats_res.status_code, status.HTTP_200_OK)
        self.assertIn('overview', stats_res.data)
        self.assertIn('total_users', stats_res.data['overview'])

    def test_admin_user_management(self):
        self.client.force_authenticate(user=self.admin_user)
        users_res = self.client.get('/api/dashboard/users/')
        self.assertEqual(users_res.status_code, status.HTTP_200_OK)

        # Toggle regular user status
        patch_res = self.client.patch(f'/api/dashboard/users/{self.regular_user.id}/', {
            'is_active': False
        })
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)
