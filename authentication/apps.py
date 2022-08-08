from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"

    def ready(self):
        from authentication.models import Role  # noqa

        admin_role = Role.objects.get_or_create(title="Admin")
        user_role = Role.objects.get_or_create(title="User")
