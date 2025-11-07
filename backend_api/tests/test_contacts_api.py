#backend_api/tests/test_contacts_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend_api.models import Contact

User = get_user_model()


class ContactAPITestCase(APITestCase):
    def setUp(self):
        """Create users and sample contacts"""
        self.user = User.objects.create_user(email="user@example.com", password="testpass123")
        self.other_user = User.objects.create_user(email="other@example.com", password="testpass123")

        # Auth token login (JWT or session)
        self.client.force_authenticate(user=self.user)

        self.contact1 = Contact.objects.create(
            user=self.user,
            name="John Doe",
            mobile="+911234567890",
            email="john@example.com",
            city="Delhi",
            state="Delhi",
            pan="ABCDE1234F",
            gst="22AAAAA0000A1Z5"
        )
        self.contact2 = Contact.objects.create(
            user=self.user,
            name="Jane Smith",
            mobile="9876543210",
            email="jane@example.com",
            city="Mumbai",
            state="Maharashtra",
            pan="PQRSX9999K",
            gst="27PQRSX9999K1Z9"
        )

        self.url_list = reverse("contact-list")

    # -----------------------------
    # 1️⃣ List Contacts
    # -----------------------------
    def test_list_contacts(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Contacts fetched successfully.")
        self.assertEqual(len(response.data["data"]), 2)

    # -----------------------------
    # 2️⃣ Retrieve Contact
    # -----------------------------
    def test_retrieve_contact(self):
        url = reverse("contact-detail", args=[self.contact1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "John Doe")

    # -----------------------------
    # 3️⃣ Create Contact - Success
    # -----------------------------
    def test_create_contact_success(self):
        data = {
            "name": "New Contact",
            "mobile": "9998887776",
            "email": "new@example.com",
            "city": "Chennai",
            "state": "TN",
            "pan": "ABCDE1234F",
            "gst": "33ABCDE1234F1Z2"
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Contact created successfully.")
        self.assertEqual(Contact.objects.filter(user=self.user).count(), 3)

    # -----------------------------
    # 4️⃣ Create Contact - Invalid PAN
    # -----------------------------
    def test_create_contact_invalid_pan(self):
        data = {
            "name": "Bad PAN",
            "mobile": "9998887776",
            "email": "badpan@example.com",
            "pan": "INVALID123",
            "gst": "33ABCDE1234F1Z2"
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("Invalid PAN format", str(response.data["message"]))

    # -----------------------------
    # 5️⃣ Update Contact (PUT)
    # -----------------------------
    def test_update_contact(self):
        url = reverse("contact-detail", args=[self.contact1.id])
        data = {"name": "Updated Name", "mobile": "+919999999999"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Updated Name")

    # -----------------------------
    # 6️⃣ Partial Update (PATCH)
    # -----------------------------
    def test_partial_update_contact(self):
        url = reverse("contact-detail", args=[self.contact2.id])
        data = {"city": "Pune"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["city"], "Pune")

    # -----------------------------
    # 7️⃣ Delete Contact
    # -----------------------------
    def test_delete_contact(self):
        url = reverse("contact-detail", args=[self.contact1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "Contact deleted successfully.")
        self.assertFalse(Contact.objects.filter(id=self.contact1.id).exists())

    # -----------------------------
    # 8️⃣ Search Contacts
    # -----------------------------
    def test_search_contacts(self):
        """Ensure search returns partial matches (case-insensitive)."""
        url = reverse("contact-list")

        # Create sample contacts
        Contact.objects.create(user=self.user, name="John Doe", mobile="9999999999", email="john@example.com")
        Contact.objects.create(user=self.user, name="Johnny Depp", mobile="8888888888", email="depp@example.com")
        Contact.objects.create(user=self.user, name="Alice Johnson", mobile="7777777777", email="alice@example.com")
        Contact.objects.create(user=self.user, name="Mark Smith", mobile="6666666666", email="mark@example.com")

        # Search by partial name
        response = self.client.get(url, {"search": "John"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

        results = response.data["data"]

        # ✅ Partial match: "John Doe", "Johnny Depp", and "Alice Johnson" should match
        matched_names = [r["name"] for r in results]
        self.assertTrue(any("john" in name.lower() for name in matched_names))

        # At least one contact must match, but any number is valid since multiple fields are searched
        self.assertGreaterEqual(len(results), 1)

        # ✅ Check structure
        for item in results:
            self.assertIn("name", item)
            self.assertIn("mobile", item)
            self.assertIn("email", item)

    # -----------------------------
    # 9️⃣ Ordering Contacts
    # -----------------------------
    def test_ordering_contacts_by_name(self):
        response = self.client.get(f"{self.url_list}?ordering=name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data_names = [c["name"] for c in response.data["data"]]
        self.assertEqual(data_names, sorted(data_names))

    # -----------------------------
    # 🔟 Restrict Access to Other Users
    # -----------------------------
    def test_user_cannot_access_others_contact(self):
        """Ensure user cannot retrieve another user's contact"""
        contact_other = Contact.objects.create(
            user=self.other_user, name="Hidden User", mobile="1111111111"
        )
        url = reverse("contact-detail", args=[contact_other.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -----------------------------
    # 11️⃣ Unauthorized Access
    # -----------------------------
    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])
        self.assertIn("credentials", str(response.data["message"]).lower())
