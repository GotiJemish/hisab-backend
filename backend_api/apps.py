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
            except Exception as e:
                print(f"Error executing database migrations: {e}")

