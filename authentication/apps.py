from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"

    def ready(self):
        from authentication.models import Role  # noqa

        user_role = Role.objects.filter(title="User").first()
        admin_role = Role.objects.filter(title="Admin").first()

        if not user_role:
            Role.objects.create(title="User")
        if not admin_role:
            Role.objects.create(title="Admin")

        return True
