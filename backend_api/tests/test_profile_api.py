# backend_api/tests/test_profile_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend_api.models.company import Company

User = get_user_model()


class ProfileAPITestCase(APITestCase):
    def setUp(self):
        """Set up companies, admin users, and regular staff users"""
        self.company = Company.objects.create(name="Acme Corporation")
        
        # Company Admin User
        self.admin = User.objects.create_user(
            email="admin@acme.com",
            password="adminpassword123",
            first_name="Admin",
            last_name="User",
            role="COMPANY_ADMIN",
            company=self.company
        )

        # Staff User in same company
        self.staff = User.objects.create_user(
            email="staff@acme.com",
            password="staffpassword123",
            first_name="Staff",
            last_name="User",
            role="STAFF",
            company=self.company
        )

        self.url_profile = reverse("user-profile")
        self.url_password = reverse("change-password")
        self.url_company = reverse("company-profile")

    def test_get_user_profile(self):
        """Verify user can retrieve their own profile details"""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.url_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)
        self.assertEqual(response.data["data"]["email"], "staff@acme.com")
        self.assertEqual(response.data["data"]["role"], "STAFF")
        self.assertEqual(response.data["data"]["company"]["name"], "Acme Corporation")

    def test_update_user_profile(self):
        """Verify user can update their first name and last name"""
        self.client.force_authenticate(user=self.staff)
        payload = {
            "first_name": "UpdatedStaff",
            "last_name": "UpdatedLastName"
        }
        response = self.client.patch(self.url_profile, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.first_name, "UpdatedStaff")
        self.assertEqual(self.staff.last_name, "UpdatedLastName")

    def test_change_password_success(self):
        """Verify password update works with correct old password"""
        self.client.force_authenticate(user=self.staff)
        payload = {
            "old_password": "staffpassword123",
            "new_password": "newsecurepassword123"
        }
        response = self.client.post(self.url_password, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify can authenticate with the new password
        self.client.logout()
        login_url = reverse("login")
        login_payload = {
            "email": "staff@acme.com",
            "password": "newsecurepassword123"
        }
        login_resp = self.client.post(login_url, login_payload, format="json")
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)

    def test_change_password_failure_incorrect_old_password(self):
        """Verify password update fails if current password is wrong"""
        self.client.force_authenticate(user=self.staff)
        payload = {
            "old_password": "wrongpassword123",
            "new_password": "newsecurepassword123"
        }
        response = self.client.post(self.url_password, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_company_profile(self):
        """Verify logged-in user can retrieve their company details"""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.url_company)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Acme Corporation")
        self.assertIn("gstin", response.data["data"])

    def test_admin_can_update_company_profile(self):
        """Verify company admin can update company info, including GSTIN"""
        self.client.force_authenticate(user=self.admin)
        payload = {
            "name": "Acme Industries Ltd",
            "phone": "9999999999",
            "email": "info@acme.com",
            "website": "https://acme.com",
            "gstin": "27AADCA1154K1Z5",  # 15 character sample GSTIN
            "address": "123 Business Park, Mumbai"
        }
        response = self.client.patch(self.url_company, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, "Acme Industries Ltd")
        self.assertEqual(self.company.gstin, "27AADCA1154K1Z5")
        self.assertEqual(self.company.phone, "9999999999")

    def test_staff_cannot_update_company_profile(self):
        """Verify non-admin users (staff) are restricted from editing company details"""
        self.client.force_authenticate(user=self.staff)
        payload = {
            "name": "Hack Acme Inc"
        }
        response = self.client.patch(self.url_company, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify no changes made
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, "Acme Corporation")

    def test_invalid_gstin_format_fails(self):
        """Verify invalid GSTIN lengths (not 15 characters) trigger validation errors"""
        self.client.force_authenticate(user=self.admin)
        payload = {
            "gstin": "INVALIDGSTIN"  # Not 15 characters
        }
        response = self.client.patch(self.url_company, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
