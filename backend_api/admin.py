from django.contrib import admin
from .models import User,Contact,Invoice,InvoiceItem

admin.site.register(User)
admin.site.register(Contact)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)


