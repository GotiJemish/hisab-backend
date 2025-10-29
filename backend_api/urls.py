# backend_api/urls.py
from django.urls import path
from .views import (
    RegisterView, VerifyOTPView, LoginView, CustomTokenObtainPairView,
    ForgotPasswordView, VerifyForgotOTPView, ResetPasswordView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-forgot-otp/', VerifyForgotOTPView.as_view(), name='verify-forgot-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
