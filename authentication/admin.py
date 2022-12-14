from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from authentication.models import Notification, Role, User


class UserCreationForm(forms.ModelForm):
    """A form for creating new users.

    Includes all the required fields, plus a repeated password.
    """

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_password2(self) -> str | None:
        """Checks if passwords are the same.

        :return: Password string.
        :raises ValidationError: if passwords don't match.
        """
        password1: str | None = self.cleaned_data.get("password1")
        password2: str | None = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit: bool = True) -> User:
        """Saves user to database with hashing his password.

        :param commit: To commit or not.
        :return: User instance.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users.

    Includes all the fields on the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "date_created",
            "profile_image",
            "role",
        )


class UserAdmin(BaseUserAdmin):
    """User model renderer in admin panel."""

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("username", "email", "date_created", "role")
    list_filter = ("username", "email", "date_created", "role")
    fieldsets = (
        (None, {"fields": ("username", "password", "date_created")}),
        ("Personal info", {"fields": ("email", "profile_image")}),
        ("Permissions", {"fields": ("role",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
    search_fields = ("username", "email")
    ordering = ("username",)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Role)
admin.site.register(Notification)
