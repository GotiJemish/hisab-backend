#backend_api/tests/test_contacts_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from backend_api.models import Invoice, InvoiceItem, Contact

User = get_user_model()


class InvoiceAPITestCase(APITestCase):

    def setUp(self):
        """Create users and initial setup"""
        self.user = User.objects.create_user(email="user@example.com", password="testpass123")
        self.other_user = User.objects.create_user(email="other@example.com", password="testpass123")

        self.client.force_authenticate(user=self.user)

        self.contact = Contact.objects.create(
            user=self.user,
            name="John Doe"
        )

        self.invoice = Invoice.objects.create(
            user=self.user,
            contact=self.contact,
            invoice_type="default",
            supply_type="regular",
        )

        self.url_list = reverse("invoice-list")  # GET, POST
        self.url_detail = lambda pk: reverse("invoice-detail", kwargs={"pk": pk})


    # ----------------------------------------------------
    # Create API Test
    # ----------------------------------------------------
    def test_invoice_create_api(self):
        payload = {
            "contact": self.contact.id,
            "invoice_type": "default",
            "supply_type": "regular",
            "items": [
                {"description": "A", "quantity": 2, "rate": 100, "discount": 0}
            ],
        }

        response = self.client.post(self.url_list, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data["data"]

        self.assertTrue(data["bill_id"].startswith("INV"))
        self.assertIsNotNone(data["invoice_number"])
        self.assertEqual(len(data["items"]), 1)


    # ----------------------------------------------------
    # List Only Current User Data
    # ----------------------------------------------------
    def test_invoice_list_only_user_data(self):
        # Create invoice for other user
        contact2 = Contact.objects.create(user=self.other_user, name="X")
        Invoice.objects.create(
            user=self.other_user,
            contact=contact2,
            invoice_type="default"
        )

        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)  # Only self.user invoices


    # ----------------------------------------------------
    # Update API Test
    # ----------------------------------------------------
    def test_invoice_update_api(self):
        payload = {
            "items": [
                {"description": "X", "quantity": 5, "rate": 100, "discount": 0}
            ]
        }

        response = self.client.patch(self.url_detail(self.invoice.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["data"]["total_amount"]), 500)


    # ----------------------------------------------------
    # Delete API Test
    # ----------------------------------------------------
    def test_invoice_delete_api(self):
        response = self.client.delete(self.url_detail(self.invoice.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Invoice.objects.count(), 0)


    # ----------------------------------------------------
    # Search API Test
    # ----------------------------------------------------
    def test_invoice_search_api(self):
        Invoice.objects.create(
            user=self.user, contact=self.contact, invoice_type="default"
        )

        response = self.client.get(f"{self.url_list}?search=john")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 2)


# --------------------------------------------------------
# Non-API Tests for Model & Serializer behavior
# --------------------------------------------------------

class InvoiceModelSerializerTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="test@ex.com")
        self.contact = Contact.objects.create(user=self.user, name="John")

    def test_invoice_item_total_calculation(self):
        item = InvoiceItem.objects.create(
            description="Test",
            quantity=5,
            rate=100,
            discount=50
        )

        self.assertEqual(float(item.total), 450)

    def test_auto_bill_id_and_invoice_number(self):
        invoice = Invoice.objects.create(
            user=self.user,
            contact=self.contact,
            invoice_type="default",
            supply_type="regular",
        )

        self.assertTrue(invoice.bill_id.startswith("INV"))
        self.assertIsNotNone(invoice.invoice_number)
        self.assertGreaterEqual(len(invoice.invoice_number), 6)

    def test_invoice_total_updates(self):
        item1 = InvoiceItem.objects.create(description="x", quantity=2, rate=100)
        item2 = InvoiceItem.objects.create(description="y", quantity=3, rate=200)

        invoice = Invoice.objects.create(
            user=self.user, contact=self.contact, invoice_type="default"
        )

        invoice.items.add(item1, item2)
        invoice.update_total()

        self.assertEqual(float(invoice.total_amount), (2 * 100) + (3 * 200))
