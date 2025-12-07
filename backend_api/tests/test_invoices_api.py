# backend_api/tests/test_invoices_api.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from backend_api.models import Invoice, Contact, InvoiceItem

User = get_user_model()


# ======================================================================
# 1) API TEST CASES (DRF style tests)
# ======================================================================

class InvoiceAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="u1@example.com", password="1234")
        self.other = User.objects.create_user(email="u2@example.com", password="1234")

        self.client.force_authenticate(user=self.user)

        self.contact = Contact.objects.create(
            user=self.user,
            name="John",
        )

        self.invoice = Invoice.objects.create(
            user=self.user,
            contact=self.contact,
            invoice_type="default",
            supply_type="regular"
        )

        self.url_list = reverse("invoice-list")
        self.url_detail = lambda pk: reverse("invoice-detail", kwargs={"pk": pk})

    # -----------------------------
    def test_invoice_create_api(self):
        payload = {
            "contact": self.contact.id,
            "invoice_type": "default",
            "supply_type": "regular",
            "items": [
                {"description": "A", "quantity": 2, "rate": 100, "discount": 10}
            ]
        }

        response = self.client.post(self.url_list, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data["data"]

        self.assertTrue(data["bill_id"].startswith("INV"))
        self.assertIsNotNone(data["invoice_number"])
        self.assertEqual(float(data["total_amount"]), (2 * 100) - 10)

    # -----------------------------
    def test_invoice_list_only_user_data(self):
        contact2 = Contact.objects.create(user=self.other, name="X")
        Invoice.objects.create(user=self.other, contact=contact2, invoice_type="default")

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data["data"]), 1)

    # -----------------------------
    def test_invoice_update_api(self):
        payload = {
            "items": [
                {"description": "Updated", "quantity": 5, "rate": 100, "discount": 0}
            ]
        }

        response = self.client.patch(self.url_detail(self.invoice.id), payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.data["data"]["total_amount"]), 500)

    # -----------------------------
    def test_invoice_delete_api(self):
        response = self.client.delete(self.url_detail(self.invoice.id))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Invoice.objects.count(), 0)

    # -----------------------------
    def test_invoice_search_api(self):
        Invoice.objects.create(user=self.user, contact=self.contact, invoice_type="default")
        response = self.client.get(f"{self.url_list}?search=john")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]), 2)

    # -----------------------------
    # New edge & advanced tests
    # -----------------------------

    def test_invoice_create_invalid_item(self):
        payload = {
            "contact": self.contact.id,
            "invoice_type": "default",
            "supply_type": "regular",
            "items": [
                {"description": "Bad Item", "quantity": -2, "rate": 100, "discount": 0},
                {"description": "Over Discount", "quantity": 1, "rate": 50, "discount": 100}
            ]
        }

        response = self.client.post(self.url_list, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", str(response.data))

    def test_invoice_create_without_items(self):
        payload = {
            "contact": self.contact.id,
            "invoice_type": "default",
            "supply_type": "regular",
            "items": []
        }

        response = self.client.post(self.url_list, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(response.data["data"]["total_amount"]), 0)

    def test_invoice_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoice_update_items_total(self):
        item1 = InvoiceItem.objects.create(description="X", quantity=1, rate=100)
        self.invoice.items.add(item1)
        self.invoice.update_total()
        self.assertEqual(float(self.invoice.total_amount), 100)

        payload = {
            "items": [
                {"description": "Y", "quantity": 3, "rate": 50, "discount": 0}
            ]
        }
        response = self.client.patch(self.url_detail(self.invoice.id), payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.data["data"]["total_amount"]), 150)

    def test_invoice_search_by_notes(self):
        self.invoice.notes = "Important project invoice"
        self.invoice.save()

        response = self.client.get(f"{self.url_list}?search=project")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]), 1)

    def test_invoice_filter_by_supply_type(self):
        Invoice.objects.create(user=self.user, contact=self.contact, invoice_type="default", supply_type="bill_to_ship_to")
        response = self.client.get(f"{self.url_list}?supply_type=bill_to_ship_to")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(i["supply_type"] == "bill_to_ship_to" for i in response.data["data"]))

    def test_invoice_partial_update_type(self):
        payload = {"invoice_type": "delivery_challan"}
        response = self.client.patch(self.url_detail(self.invoice.id), payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["invoice_type"], "delivery_challan")

    def test_invoice_delete_non_existent(self):
        url = self.url_detail(9999)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_multiple_invoice_number_increment(self):
        invoice1 = Invoice.objects.create(user=self.user, contact=self.contact, invoice_type="default")
        invoice2 = Invoice.objects.create(user=self.user, contact=self.contact, invoice_type="default")

        self.assertNotEqual(invoice1.bill_id, invoice2.bill_id)
        self.assertNotEqual(invoice1.invoice_number, invoice2.invoice_number)


# ======================================================================
# 2) MODEL TESTS
# ======================================================================

class InvoiceModelTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="test@example.com")
        self.contact = Contact.objects.create(user=self.user, name="John")

    def test_invoice_item_total_calculation(self):
        item = InvoiceItem.objects.create(
            description="Test", quantity=5, rate=100, discount=50
        )
        self.assertEqual(float(item.total), 450)

    def test_invoice_auto_generates_ids(self):
        invoice = Invoice.objects.create(
            user=self.user, contact=self.contact, invoice_type="default", supply_type="regular"
        )
        self.assertTrue(invoice.bill_id.startswith("INV"))
        self.assertIsNotNone(invoice.invoice_number)

    def test_invoice_total_updates(self):
        item1 = InvoiceItem.objects.create(description="X", quantity=2, rate=100)
        item2 = InvoiceItem.objects.create(description="Y", quantity=3, rate=200)

        invoice = Invoice.objects.create(
            user=self.user, contact=self.contact, invoice_type="default"
        )
        invoice.items.add(item1, item2)
        invoice.update_total()

        self.assertEqual(float(invoice.total_amount), (2*100) + (3*200))


# ======================================================================
# 3) SERIALIZER VALIDATION TESTS
# ======================================================================

class InvoiceSerializerValidationTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="u@example.com")
        self.contact = Contact.objects.create(user=self.user, name="John")

    def test_invalid_invoice_type(self):
        from backend_api.serializers.invoice import InvoiceSerializer

        ser = InvoiceSerializer(
            data={
                "contact": self.contact.id,
                "invoice_type": "xyz",   # Invalid
                "supply_type": "regular",
                "items": []
            },
            context={"request": type("req", (), {"user": self.user})}
        )

        self.assertFalse(ser.is_valid())
        self.assertIn('"xyz" is not a valid choice.', str(ser.errors))


# ======================================================================
# 4) PYTEST TESTS (ordering, filtering, pagination, bill-id, invoice-number)
# ======================================================================

class TestInvoiceAdvanced:

    def setup_user(self):
        user = User.objects.create_user(email="test@example.com", password="pass1234")
        contact = Contact.objects.create(user=user, name="Test Contact", mobile="1234567890")
        return user, contact

    def auth_client(self, setup_user):
        user, _ = setup_user
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    # ORDERING ---------------------------------------------------------
    def test_order_by_amount(self, auth_client, setup_user):
        user, contact = setup_user
        url = reverse("invoice-list")

        Invoice.objects.create(user=user, contact=contact, invoice_type="default", total_amount=100)
        Invoice.objects.create(user=user, contact=contact, invoice_type="default", total_amount=500)

        res = auth_client.get(url + "?ordering=total_amount")
        amounts = [float(i["total_amount"]) for i in res.data["data"]]
        assert amounts == sorted(amounts)

        res = auth_client.get(url + "?ordering=-total_amount")
        amounts = [float(i["total_amount"]) for i in res.data["data"]]
        assert amounts == sorted(amounts, reverse=True)

    # FILTERING --------------------------------------------------------
    def test_filter_invoice_type(self, auth_client, setup_user):
        user, contact = setup_user
        url = reverse("invoice-list")

        Invoice.objects.create(user=user, contact=contact, invoice_type="default")
        Invoice.objects.create(user=user, contact=contact, invoice_type="delivery_challan")

        res = auth_client.get(url + "?invoice_type=default")
        assert all(i["invoice_type"] == "default" for i in res.data["data"])

    def test_filter_date_range(self, auth_client, setup_user):
        user, contact = setup_user
        url = reverse("invoice-list")

        d1 = timezone.now().date().replace(day=1)
        d2 = timezone.now().date()

        Invoice.objects.create(user=user, contact=contact, invoice_type="default", invoice_date=d1)
        Invoice.objects.create(user=user, contact=contact, invoice_type="default", invoice_date=d2)

        res = auth_client.get(url + f"?invoice_date__gte={d1}&invoice_date__lte={d2}")
        assert len(res.data["data"]) == 2

        res = auth_client.get(url + f"?invoice_date__gte={d2}")
        assert len(res.data["data"]) == 1

    def test_filter_amount_range(self, auth_client, setup_user):
        user, contact = setup_user
        url = reverse("invoice-list")

        Invoice.objects.create(user=user, contact=contact, invoice_type="default", total_amount=100)
        Invoice.objects.create(user=user, contact=contact, invoice_type="default", total_amount=900)

        res = auth_client.get(url + "?total_amount__gte=200&total_amount__lte=1000")
        amounts = [float(i["total_amount"]) for i in res.data["data"]]

        assert amounts == [900.0]

    # PAGINATION -------------------------------------------------------
    def test_pagination(self, auth_client, setup_user):
        user, contact = setup_user
        url = reverse("invoice-list")

        for _ in range(15):
            Invoice.objects.create(user=user, contact=contact, invoice_type="default")

        res = auth_client.get(url + "?page=1&page_size=10")
        assert len(res.data["results"]) == 10
        assert res.data["count"] == 15

    # SEARCH -----------------------------------------------------------
    def test_search(self, auth_client, setup_user):
        user, contact = setup_user
        url = reverse("invoice-list")

        Invoice.objects.create(user=user, contact=contact, invoice_type="default")
        res = auth_client.get(url + "?search=Test")

        assert res.status_code == 200
        assert len(res.data["data"]) == 1

    # BILL-ID ----------------------------------------------------------
    def test_bill_id_format(self, auth_client, setup_user):
        user, contact = setup_user
        invoice = Invoice.objects.create(user=user, contact=contact, invoice_type="default")

        today = timezone.now().date().strftime("%d%m%y")
        assert invoice.bill_id.startswith(f"INV{today}-")

        suffix = invoice.bill_id.split("-")[-1]
        assert len(suffix) == 4 and suffix.isdigit()

    # INVOICE NUMBER ---------------------------------------------------
    def test_invoice_number_generation(self, auth_client, setup_user):
        user, contact = setup_user
        today = timezone.now().date()

        invoice = Invoice.objects.create(
            user=user, contact=contact, invoice_type="default", invoice_date=today
        )

        prefix = today.strftime("%b").upper()
        yydd = today.strftime("%y%d")

        assert invoice.invoice_number.startswith(f"{prefix}-{yydd}")

        last4 = invoice.invoice_number[-4:]
        assert last4.isdigit()
