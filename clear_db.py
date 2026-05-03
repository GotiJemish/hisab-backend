import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisab_backend.settings')
django.setup()

from backend_api.models import Company, Contact, EmailOTP, Invoice, InvoiceItem, Items, User
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry

print("Starting to clear the database...")

# Clear primary application data
items_count, _ = InvoiceItem.objects.all().delete()
inv_count, _ = Invoice.objects.all().delete()
contact_count, _ = Contact.objects.all().delete()
p_items_count, _ = Items.objects.all().delete()
otp_count, _ = EmailOTP.objects.all().delete()

# Delete all users EXCEPT superusers
users_count, _ = User.objects.filter(is_superuser=False).delete()

# Delete all companies (Since the foreign key uses SET_NULL, superadmins' company fields will just be set to None)
company_count, _ = Company.objects.all().delete()

# Clear inactive sessions and admin log histories
Session.objects.all().delete()
LogEntry.objects.all().delete()

print("--- Database Cleanup Summary ---")
print(f"Deleted {users_count} Users (Non-Admins)")
print(f"Deleted {company_count} Companies")
print(f"Deleted {inv_count} Invoices & {items_count} Invoice Items")
print(f"Deleted {contact_count} Contacts, {p_items_count} Items, {otp_count} OTPs")
print("Superadmin data has been PRESERVED successfully!")
