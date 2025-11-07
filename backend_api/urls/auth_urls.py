# backend_api/urls/auth_urls.py
from django.urls import path
from backend_api.views import (
    RegisterView, VerifyRegisterOTPView, LoginView, CustomTokenObtainPairView,
    ForgotPasswordView, VerifyForgotOTPView, ResetPasswordView,SetPasswordView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/register/', VerifyRegisterOTPView.as_view(), name='verify-register-otp'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-otp/forgot-password/', VerifyForgotOTPView.as_view(), name='verify-forgot-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
