from django.urls import path
from .views import RegisterView,AddContactView, LoginView, VerifyOTPView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),

    # JWT authentication endpoints
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path('login/', LoginView.as_view(), name='login'),

    path('contacts/add/', AddContactView.as_view(), name='add-contact'),
]
