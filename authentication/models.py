from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.validators import validate_email
from django.db import models
from django.utils import timezone


class Role(models.Model):
    """Model for database table 'role'."""

    title = models.CharField(max_length=128, unique=True)

    def __str__(self) -> str:
        return self.title


class UserManager(BaseUserManager["User"]):
    """Custom user manager."""

    def create_user(
        self,
        username: str,
        email: str,
        password: str | None = None,
    ) -> "User":
        """Creates and saves a User with the given username, email and password.

        :param username: User's username field.
        :param email: User's email field.
        :param password: User's password field.
        :return: User instance.
        :raises ValueError: if username or email was not provided.
        """
        if not username:
            raise ValueError("Users must have a username")
        if not email:
            raise ValueError("Users must have an email address")

        validate_email(email)

        role, _ = Role.objects.get_or_create(title="Admin")
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        email: str,
        password: str | None = None,
    ) -> "User":
        """Creates and saves a superuser with the given username, email and password.

        :param username: Superuser's username field.
        :param email: Superuser's email field.
        :param password: Superuser's password field.
        :return: User instance.
        """
        user = self.create_user(username, email, password)
        user.role, _ = Role.objects.get_or_create(title="Admin")
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Custom user model."""

    username = models.CharField(max_length=128, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    date_created = models.DateTimeField(default=timezone.now)
    profile_image = models.CharField(
        max_length=128,
        default="https://i.imgur.com/2VVImvn.jpg",
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="users")

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return self.username

    @property
    def is_superuser(self) -> bool:
        """Is user admin or not.

        :return: True - user is an admin, False - user is not an admin.
        """
        return self.role.title == "Admin"

    @property
    def is_staff(self) -> bool:
        """Is user a staff or not.

        :return: True - user is a staff, False - user is not a staff.
        """
        return self.is_superuser

    @staticmethod
    def has_perm(perm, obj=None) -> bool:
        """Does the user have a specific permission?"""
        return True

    @staticmethod
    def has_module_perms(app_label) -> bool:
        """Does the user have permissions to view the app `app_label`?"""
        return True


class Notification(models.Model):
    """Model for database table 'notification'."""

    title = models.CharField(max_length=256)
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    question = models.ForeignKey(
        "forum.Question",
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    def __str__(self) -> str:
        return self.title
