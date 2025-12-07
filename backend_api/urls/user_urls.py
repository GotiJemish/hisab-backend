# backend_api/urls/user_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from backend_api.views import ContactViewSet, ItemsViewSet,InvoiceViewSet


router = DefaultRouter()



# GET	/contacts/	List all contacts of logged-in user
# POST	/contacts/	Create a new contact
# GET	/contacts/<id>/	Retrieve specific contact
# PUT	/contacts/<id>/	Update all fields
# PATCH	/contacts/<id>/	Update partial fields
# DELETE	/contacts/<id>/	Delete a contact
# GET /contacts/?search=John
# GET /contacts/?ordering=name
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'items', ItemsViewSet, basename='item')
router.register(r'invoices', InvoiceViewSet, basename='invoice')



urlpatterns = [
    path('', include(router.urls)),
    path("invoices/invoice-number/", InvoiceViewSet.as_view({"get": "next_invoice_number"})),
]
