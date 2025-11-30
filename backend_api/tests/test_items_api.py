# backend_api/tests/test_items_api.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend_api.models import Items

User = get_user_model()


class ItemsAPITestCase(APITestCase):

    def setUp(self):
        # Users
        self.user = User.objects.create_user(email="user1@example.com", password="1234")
        self.other_user = User.objects.create_user(email="user2@example.com", password="1234")

        self.client.force_authenticate(user=self.user)

        # Items
        self.item1 = Items.objects.create(user=self.user, name="Item 1", rate=100)
        self.item2 = Items.objects.create(user=self.user, name="Item 2", rate=200)
        self.item_other = Items.objects.create(user=self.other_user, name="Other Item", rate=300)

        # URL helpers (must match router basename='items')
        self.url_list = reverse("items-list")
        self.url_detail = lambda pk: reverse("items-detail", kwargs={"pk": pk})

    # -----------------------------
    # CREATE
    # -----------------------------
    def test_create_item(self):
        payload = {
            "name": "New Item",
            "type": "product",
            "unit_type": "Pcs",
            "tax_category": "gst-5",
            "rate": 150,
            "discount": 10,
            "with_tax": False,
        }
        response = self.client.post(self.url_list, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data["data"]
        self.assertEqual(data["name"], "New Item")
        self.assertEqual(float(data["rate"]), 150)
        self.assertEqual(float(data["discount"]), 10)

    def test_create_item_invalid_rate_discount(self):
        payload = {"name": "Invalid Item", "rate": -10, "discount": -5}
        response = self.client.post(self.url_list, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Rate cannot be negative", str(response.data))
        self.assertIn("Discount cannot be negative", str(response.data))

    # -----------------------------
    # LIST
    # -----------------------------
    def test_list_items_only_user_data(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        data = response.data["data"]
        self.assertEqual(len(data), 2)  # Only user's items
        self.assertNotIn("Other Item", [i["name"] for i in data])

    # -----------------------------
    # RETRIEVE
    # -----------------------------
    def test_retrieve_item(self):
        response = self.client.get(self.url_detail(self.item1.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["name"], self.item1.name)

    # -----------------------------
    # UPDATE
    # -----------------------------
    def test_update_item(self):
        payload = {"name": "Updated Item 1", "rate": 999}
        response = self.client.put(self.url_detail(self.item1.id), payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["name"], "Updated Item 1")
        self.assertEqual(float(response.data["data"]["rate"]), 999)

    def test_partial_update_item(self):
        payload = {"rate": 555}
        response = self.client.patch(self.url_detail(self.item1.id), payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.data["data"]["rate"]), 555)

    # -----------------------------
    # DELETE
    # -----------------------------
    def test_delete_item(self):
        response = self.client.delete(self.url_detail(self.item1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Items.objects.filter(id=self.item1.id).exists())

    # -----------------------------
    # VALIDATIONS
    # -----------------------------
    def test_name_cannot_be_empty(self):
        payload = {"name": "   ", "rate": 10}
        response = self.client.post(self.url_list, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Item name cannot be empty", str(response.data))

    def test_discount_cannot_exceed_rate(self):
        payload = {"name": "Test Item", "rate": 50, "discount": 100}
        response = self.client.post(self.url_list, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Discount cannot be greater than rate", str(response.data))

    # -----------------------------
    # SEARCH / ORDERING
    # -----------------------------
    def test_search_items(self):
        response = self.client.get(f"{self.url_list}?search=Item 1")
        self.assertEqual(response.status_code, 200)
        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Item 1")

    def test_ordering_items(self):
        response = self.client.get(f"{self.url_list}?ordering=rate")
        self.assertEqual(response.status_code, 200)
        rates = [float(i["rate"]) for i in response.data["data"]]
        self.assertEqual(rates, sorted(rates))
