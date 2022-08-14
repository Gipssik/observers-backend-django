from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Authentication app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"

    def ready(self) -> None:
        """Create basic roles on startup."""
        from authentication.models import Role

        Role.objects.get_or_create(title="Admin")
        Role.objects.get_or_create(title="User")
