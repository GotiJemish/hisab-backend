from django.core.management.base import BaseCommand
from backend_api.models import User, Company

class Command(BaseCommand):
    help = 'Migrates existing standalone users to their own Company (Organizations)'

    def handle(self, *args, **kwargs):
        users = User.objects.filter(company__isnull=True)
        count = 0
        for user in users:
            # Create a company named after them
            company_name = f"{user.first_name} {user.last_name} Company".strip()
            if not company_name or company_name == "Company":
                company_name = f"{user.email}'s Company"
                
            company = Company.objects.create(name=company_name)
            user.company = company
            user.role = 'COMPANY_ADMIN'
            user.save()
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully migrated {count} users into Companies!'))
