import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisab_backend.settings')
django.setup()

from backend_api.models import Company, Contact, EmailOTP, Invoice, InvoiceItem, Items, User, Challan, ChallanItem, Tax, Account, Income, Expense, Role
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry

print("Starting to clear the database...")

# Clear primary application data
ChallanItem.objects.all().delete()
Challan.objects.all().delete()
InvoiceItem.objects.all().delete()
Invoice.objects.all().delete()
Contact.objects.all().delete()
Items.objects.all().delete()
EmailOTP.objects.all().delete()
Income.objects.all().delete()
Expense.objects.all().delete()
Account.objects.all().delete()
Role.objects.all().delete()
Tax.objects.all().delete()

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
print("All application data tables (invoices, challans, contacts, items, accounts, roles, taxes) cleared successfully!")
print("Superadmin data has been PRESERVED successfully!")
