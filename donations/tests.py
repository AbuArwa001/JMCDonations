from django.test import TestCase

from donations.serializers import DonationSerializer
from categories.models import Categories
from users.models import Users


class DonationSerializerTest(TestCase):
    def setUp(self):
        self.user = Users.objects.create_user(username="testuser", password="testpass")
        self.category = Categories.objects.create(name="Education")

        self.valid_data = {
            "title": "School Supplies Fund",
            "description": "Buy school supplies for children in need",
            "paybill_number": "123456",
            "account_name": "SchoolFund",
            "target_amount": "5000.00",
            "start_date": "2025-11-27T07:48:20.991862Z",
            "end_date": "2026-02-25T07:48:20.991862Z",
            "status": "Active",
            "category": self.category.id,
        }

    def test_valid_serialization(self):
        serializer = DonationSerializer(data=self.valid_data, context={"request": None})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_required_field(self):
        invalid_data = self.valid_data.copy()
        invalid_data.pop("title")
        serializer = DonationSerializer(data=invalid_data, context={"request": None})
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
