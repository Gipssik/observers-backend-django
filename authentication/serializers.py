from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from authentication.models import User, Role


class TokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs) -> dict[str, str]:
        """Changes structure of token to {'access_token': ..., 'token_type': ...}."""

        super().validate(attrs)
        refresh = self.get_token(self.user)
        data = {
            "access_token": str(refresh.access_token),
            "token_type": "bearer",
        }
        return data


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["title"]


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data: dict) -> User:
        user_role, _ = Role.objects.get_or_create(title="User")
        validated_data.update({"role": user_role})
        u = User(**validated_data)
        u.set_password(validated_data["password"])
        u.save()
        return u


class UserChangeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(required=False, validators=[validate_password])
    profile_image = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ["email", "password", "profile_image"]

    def update(self, instance: User, validated_data: dict) -> User:
        instance.email = validated_data.get("email", instance.email)
        if new_password := validated_data.get("password"):
            instance.set_password(new_password)
        instance.profile_image = validated_data.get(
            "profile_image", instance.profile_image
        )
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "email", "date_created", "profile_image", "role"]
