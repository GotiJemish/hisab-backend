from django.contrib import admin
from .models import User, Contact, Invoice, InvoiceItem, Items, Company, EmailOTP

admin.site.register(User)
admin.site.register(Contact)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Items)
admin.site.register(Company)
admin.site.register(EmailOTP)
