from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from lost_items.models import LostItem
from found_items.models import FoundItem
from ai_matching.services import (
    calculate_cosine_similarity,
    calculate_category_similarity,
    calculate_color_similarity,
    calculate_text_similarity,
    compute_weighted_match_score
)

User = get_user_model()

class AIMatchingServiceTests(TestCase):
    def setUp(self):
        self.user_lost = User.objects.create_user(username='lost_user', password='pass123Password')
        self.user_found = User.objects.create_user(username='found_user', password='pass123Password')

    def test_cosine_similarity(self):
        v1 = [1.0, 0.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        v3 = [0.0, 1.0, 0.0]
        self.assertAlmostEqual(calculate_cosine_similarity(v1, v2), 1.0, places=2)
        self.assertAlmostEqual(calculate_cosine_similarity(v1, v3), 0.5, places=2)

    def test_category_similarity(self):
        self.assertEqual(calculate_category_similarity('ELECTRONICS', 'ELECTRONICS'), 1.0)
        self.assertEqual(calculate_category_similarity('WALLETS_PURSE', 'BAGS_LUGGAGE'), 0.5)
        self.assertEqual(calculate_category_similarity('PETS', 'ELECTRONICS'), 0.0)

    def test_color_similarity(self):
        self.assertEqual(calculate_color_similarity('Black', 'black'), 1.0)
        self.assertEqual(calculate_color_similarity('Dark Blue', 'blue'), 0.75)
        self.assertEqual(calculate_color_similarity('Charcoal', 'black'), 0.6)
        self.assertEqual(calculate_color_similarity('Red', 'Green'), 0.0)

    def test_text_similarity(self):
        sim = calculate_text_similarity('Black Apple iPhone 14', 'Lost near library', 'Found Apple iPhone', 'Phone on desk')
        self.assertGreater(sim, 0.1)

    def test_weighted_matching_score_calculation(self):
        lost = LostItem.objects.create(
            user=self.user_lost,
            item_name="Dell XPS 15 Laptop",
            category="ELECTRONICS",
            description="Silver metal laptop with sticker on lid",
            colour="Silver",
            date_lost=date.today(),
            location="Tech Park",
            latitude=17.44,
            longitude=78.37
        )
        found = FoundItem.objects.create(
            user=self.user_found,
            item_name="Silver Laptop Dell",
            category="ELECTRONICS",
            description="Silver laptop found at Tech Park cafeteria",
            colour="Silver",
            date_found=date.today(),
            found_location="Tech Park Cafeteria",
            latitude=17.441,
            longitude=78.371
        )
        scores = compute_weighted_match_score(lost, found)
        self.assertIn('total_score', scores)
        self.assertIn('match_label', scores)
        self.assertGreaterEqual(scores['category_similarity'], 1.0)
        self.assertGreaterEqual(scores['color_similarity'], 0.6)
