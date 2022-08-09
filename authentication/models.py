from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import validate_email
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username: str, email: str, password: str = None) -> "User":
        """Creates and saves a User with the given username, email and password."""

        if not username:
            raise ValueError("Users must have a username")
        if not email:
            raise ValueError("Users must have an email address")

        validate_email(email)

        role = Role.objects.filter(title="User").first()
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username: str, email: str, password: str = None
    ) -> "User":
        """Creates and saves a superuser with the given username, email and password."""

        user = self.create_user(username, email, password)
        user.role = Role.objects.filter(title="Admin").first()
        user.save(using=self._db)
        return user


class Role(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class User(AbstractBaseUser):
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

    def __str__(self):
        return self.username

    @property
    def is_superuser(self):
        return self.role.title == "Admin"

    @staticmethod
    def has_perm(perm, obj=None) -> bool:
        """Does the user have a specific permission?"""
        return True

    @staticmethod
    def has_module_perms(app_label) -> bool:
        """Does the user have permissions to view the app `app_label`?"""
        return True

    @property
    def is_staff(self) -> bool:
        """Is the user a member of staff?"""
        return self.is_superuser
