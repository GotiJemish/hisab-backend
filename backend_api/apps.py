from django.apps import AppConfig


class BackendApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend_api"

    def ready(self):
        import os
        # Only run migrations in the main dev-server thread, avoiding running twice
        if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('RUN_MAIN'):
            from django.core.management import call_command
            try:
                print("Running database migrations programmatically...")
                call_command('makemigrations', 'backend_api')
                call_command('migrate')
                print("Database migrations applied successfully!")
                
                # Ensure system super admin exists
                from backend_api.models import User
                superuser_email = "superuser@123"
                superuser_pass = "Jem@9878"
                if not User.objects.filter(email=superuser_email).exists():
                    print(f"Creating system super admin {superuser_email}...")
                    User.objects.create_superuser(
                        email=superuser_email,
                        password=superuser_pass,
                        first_name="System",
                        last_name="Superuser",
                        is_active=True,
                        is_verified=True,
                        role="SUPER_ADMIN"
                    )
                    print("System super admin created!")
                else:
                    su = User.objects.get(email=superuser_email)
                    su.set_password(superuser_pass)
                    su.role = "SUPER_ADMIN"
                    su.is_active = True
                    su.is_verified = True
                    su.save()
                    print("System super admin checked/updated!")
            except Exception as e:
                print(f"Error executing database migrations: {e}")

