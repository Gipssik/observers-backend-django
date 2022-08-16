from typing import Any

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from authentication.models import Notification, Role, User
from forum.models import Question


class TokenObtainSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer."""

    def validate(self, attrs: dict[str, str]) -> dict[str, str]:
        """Changes structure of token to {'access_token': ..., 'token_type': ...}.

        :param attrs: User credentials.
        :return: Dict containing access token and its type.
        """
        super().validate(attrs)
        refresh = self.get_token(self.user)
        return {
            "access_token": str(refresh.access_token),
            "token_type": "bearer",
        }


class UserCreationSerializer(serializers.ModelSerializer[User]):
    """Handles user creation."""

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data: dict[str, Any]) -> User:
        """Creates a user.

        :param validated_data: User data.
        :return: User instance.
        """
        user_role, _ = Role.objects.get_or_create(title="User")
        validated_data["role"] = user_role
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserChangeSerializer(serializers.ModelSerializer[User]):
    """Handles user change."""

    password = serializers.CharField(required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = ["email", "password", "profile_image"]

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Updates a user.

        :param instance: User instance.
        :param validated_data: New user data.
        :return: Update user instance.
        """
        if not validated_data:
            return instance

        instance.email = validated_data.get("email", instance.email)
        if new_password := validated_data.get("password"):
            instance.set_password(new_password)
        instance.profile_image = validated_data.get(
            "profile_image",
            instance.profile_image,
        )
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer[User]):
    """Handles user retrieving."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "date_created", "profile_image", "role"]
        depth = 1


class RoleBaseSerializer(serializers.ModelSerializer[Role]):
    """Handles role creation and change."""

    class Meta:
        model = Role
        fields = ["title"]


class RoleSerializer(serializers.ModelSerializer[Role]):
    """Handles role retrieving."""

    users = UserSerializer(many=True)

    class Meta:
        model = Role
        fields = ["id", "title", "users"]


class NotificationBaseSerializer(serializers.ModelSerializer[Notification]):
    """Handles create and update operations."""

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
    )
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(),
        source="question",
    )

    class Meta:
        model = Notification
        fields = ["title", "user_id", "question_id"]


class NotificationSerializer(serializers.ModelSerializer[Notification]):
    """Handles notification retrieving."""

    user_id = serializers.PrimaryKeyRelatedField(read_only=True)
    question_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Notification
        exclude = ["user", "question"]
