# backend_api/urls/user_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from backend_api.views import ContactViewSet, ItemsViewSet

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

urlpatterns = [
    path('', include(router.urls)),
]
