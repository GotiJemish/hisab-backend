# backend_api/tests/test_auth_flow.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from backend_api.models import User, EmailOTP
from django.core import mail


class AuthAPITestCase(APITestCase):
    def setUp(self):
        """Common setup for all test cases"""
        self.register_url = reverse('register')
        self.verify_register_otp_url = reverse('verify-register-otp')
        self.set_password_url = reverse('set-password')
        self.login_url = reverse('login')
        self.forgot_password_url = reverse('forgot-password')
        self.verify_forgot_otp_url = reverse('verify-forgot-otp')
        self.reset_password_url = reverse('reset-password')

        self.email = "test@example.com"
        self.password = "testpass123"

    # -------------------------------
    # 1️⃣ REGISTER USER TESTS
    # -------------------------------
    def test_register_user_success(self):
        """User registration should create an inactive user and send OTP"""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": self.email
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(email=self.email).exists())
        self.assertEqual(len(mail.outbox), 1)  # OTP sent
        self.assertIn("OTP sent", response.data["message"])

    def test_register_existing_verified_user(self):
        """Registering with verified email should fail"""
        user = User.objects.create(email=self.email, is_active=True, is_verified=True)
        data = {"first_name": "A", "last_name": "B", "email": self.email}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------
    # 2️⃣ VERIFY REGISTER OTP
    # -------------------------------
    def test_verify_register_otp_success(self):
        """Should verify OTP and activate user"""
        user = User.objects.create(email=self.email, is_active=False)
        otp_entry = EmailOTP.objects.create(user=user, otp="123456", purpose="register")

        data = {"email": self.email, "otp": "123456"}
        response = self.client.post(self.verify_register_otp_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_active)
        self.assertFalse(EmailOTP.objects.filter(user=user, purpose="register").exists())

    def test_verify_register_otp_invalid(self):
        """Invalid OTP should fail"""
        user = User.objects.create(email=self.email)
        EmailOTP.objects.create(user=user, otp="111111", purpose="register")

        data = {"email": self.email, "otp": "999999"}
        response = self.client.post(self.verify_register_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------
    # 3️⃣ SET PASSWORD
    # -------------------------------
    def test_set_password_success(self):
        """Should set password after verification"""
        user = User.objects.create(email=self.email, is_verified=True)
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.set_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.check_password(self.password))

    def test_set_password_unverified_user(self):
        """Should fail if user not verified"""
        user = User.objects.create(email=self.email, is_verified=False)
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.set_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------
    # 4️⃣ LOGIN
    # -------------------------------
    def test_login_success(self):
        """Should return JWT tokens"""
        user = User.objects.create(email=self.email, is_verified=True, is_active=True)
        user.set_password(self.password)
        user.save()

        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data["data"])

    def test_login_invalid_credentials(self):
        """Invalid password should fail"""
        user = User.objects.create(email=self.email, is_verified=True)
        user.set_password(self.password)
        user.save()

        data = {"email": self.email, "password": "wrongpass"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unverified_user(self):
        """Unverified user should not log in"""
        user = User.objects.create(email=self.email, is_verified=False)
        user.set_password(self.password)
        user.save()

        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------
    # 5️⃣ FORGOT PASSWORD
    # -------------------------------
    def test_forgot_password_success(self):
        """Should send OTP for password reset"""
        user = User.objects.create(email=self.email, is_active=True)
        data = {"email": self.email}
        response = self.client.post(self.forgot_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(EmailOTP.objects.filter(user=user, purpose="forgot").exists())
        self.assertEqual(len(mail.outbox), 1)

    def test_forgot_password_no_user(self):
        """Should fail if no active user"""
        data = {"email": "nouser@example.com"}
        response = self.client.post(self.forgot_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------
    # 6️⃣ VERIFY FORGOT OTP
    # -------------------------------
    def test_verify_forgot_otp_success(self):
        """Should verify forgot password OTP"""
        user = User.objects.create(email=self.email)
        otp_entry = EmailOTP.objects.create(user=user, otp="654321", purpose="forgot")
        data = {"email": self.email, "otp": "654321"}
        response = self.client.post(self.verify_forgot_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        otp_entry.refresh_from_db()
        self.assertTrue(otp_entry.is_verified)

    def test_verify_forgot_otp_invalid(self):
        """Invalid OTP should fail"""
        user = User.objects.create(email=self.email)
        EmailOTP.objects.create(user=user, otp="111111", purpose="forgot")

        data = {"email": self.email, "otp": "999999"}
        response = self.client.post(self.verify_forgot_otp_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------------
    # 7️⃣ RESET PASSWORD
    # -------------------------------
    def test_reset_password_success(self):
        """Should reset password if OTP verified"""
        user = User.objects.create(email=self.email)
        EmailOTP.objects.create(user=user, otp="111111", purpose="forgot", is_verified=True)

        data = {"email": self.email, "new_password": self.password}
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.check_password(self.password))

    def test_reset_password_without_verified_otp(self):
        """Should fail if OTP not verified"""
        user = User.objects.create(email=self.email)
        EmailOTP.objects.create(user=user, otp="111111", purpose="forgot", is_verified=False)

        data = {"email": self.email, "new_password": self.password}
        response = self.client.post(self.reset_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
