from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from found_items.models import FoundItem
from claims.models import ClaimRequest

User = get_user_model()

class ClaimsWorkflowTests(TestCase):
    def setUp(self):
        self.finder = User.objects.create_user(username='finder_user', password='Password123!', role='ITEM_FINDER')
        self.claimant = User.objects.create_user(username='claimant_user', password='Password123!', role='GENERAL_USER')
        self.stranger = User.objects.create_user(username='stranger_user', password='Password123!', role='GENERAL_USER')

        self.found_item = FoundItem.objects.create(
            user=self.finder,
            item_name="Found Silver Ring",
            category="JEWELRY_WATCHES",
            description="Silver ring with gemstone",
            colour="Silver",
            date_found=date.today(),
            found_location="University Campus"
        )

        self.client = APIClient()

    def test_claim_submission_and_privacy_redaction(self):
        # 1. Claimant submits claim
        self.client.force_authenticate(user=self.claimant)
        claim_payload = {
            'found_item': self.found_item.id,
            'claim_description': "I lost this ring during chemistry lab.",
            'secret_identifying_answers': "Has engraving 'Forever 2024' inside band"
        }
        res = self.client.post('/api/claims/', claim_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        claim_id = res.data['id']

        # 2. Claimant can see their secret identifying answers
        claim_res = self.client.get(f'/api/claims/{claim_id}/')
        self.assertIn("Forever 2024", claim_res.data['secret_identifying_answers'])

        # 3. Finder can see the secret verification answers to verify genuine ownership
        self.client.force_authenticate(user=self.finder)
        finder_view = self.client.get(f'/api/claims/{claim_id}/')
        self.assertIn("Forever 2024", finder_view.data['secret_identifying_answers'])

        # 4. Finder approves the claim
        patch_res = self.client.patch(f'/api/claims/{claim_id}/status/', {
            'status': 'APPROVED',
            'response_notes': 'Verification engraving matches. Ready to hand over.'
        }, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data['claim']['status'], 'APPROVED')

        # 5. Stranger cannot see the secret verification answers
        self.client.force_authenticate(user=self.stranger)
        # Note: Stranger query returns 404 because queryset only shows claims relevant to the user
        stranger_view = self.client.get(f'/api/claims/{claim_id}/')
        self.assertEqual(stranger_view.status_code, status.HTTP_404_NOT_FOUND)
