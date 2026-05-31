# backend_api/urls/user_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from backend_api.views import ContactViewSet, ItemsViewSet, InvoiceViewSet, AccountViewSet, IncomeViewSet, ExpenseViewSet
from backend_api.views.user_views import UserViewSet
from backend_api.views.role_views import RoleViewSet
from backend_api.views.tax_views import TaxViewSet

router = DefaultRouter()

# GET	/contacts/	List all contacts of logged-in user
# POST	/contacts/	Create a new contact
# GET	/contacts/<id>/	Retrieve specific contact
# PUT	/contacts/<id>/	Update all fields
# PATCH	/contacts/<id>/	Update partial fields
# DELETE	/contacts/<id>/	Delete a contact
# GET /contacts/?search=John
# GET /contacts/?ordering=name
router.register(r"contacts", ContactViewSet, basename="contact")
router.register(r"items", ItemsViewSet, basename="items")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"users", UserViewSet, basename="user")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"taxes", TaxViewSet, basename="tax")
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"incomes", IncomeViewSet, basename="income")
router.register(r"expenses", ExpenseViewSet, basename="expense")

urlpatterns = [
    path("", include(router.urls)),
]
