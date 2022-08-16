import contextlib
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import QuerySet
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from api.authentication import serializers as auth_serializers
from api.authentication.permissions import (
    CanChangeUserOrReadOnly,
    IsAdminOrNotificationDeletionByOwner,
)
from authentication.models import Notification, Role, User
from common import mixins as common_mixins


class TokenObtainView(TokenObtainPairView):
    """Custom JWT authentication view."""

    serializer_class = auth_serializers.TokenObtainSerializer


class RoleViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    """Set of role views."""

    queryset = Role.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.serializer_action_classes = {
            "list": auth_serializers.RoleSerializer,
            "create": auth_serializers.RoleBaseSerializer,
            "retrieve": auth_serializers.RoleSerializer,
            "update": auth_serializers.RoleBaseSerializer,
            "partial_update": auth_serializers.RoleBaseSerializer,
        }

    def get_queryset(self):
        """Returns queryset of roles with prefetched users.

        :return: Queryset of roles with prefetched users.
        """
        return Role.objects.all().prefetch_related("users")


class UserViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    """Set of user views."""

    queryset = User.objects.all()
    serializer_class = auth_serializers.UserSerializer
    permission_classes = [CanChangeUserOrReadOnly]
    lookup_value_regex = r"[\w@.-]+"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serializer_action_classes = {
            "create": auth_serializers.UserCreationSerializer,
            "update": auth_serializers.UserChangeSerializer,
            "partial_update": auth_serializers.UserChangeSerializer,
        }

    @property
    def paginator(self) -> Any:
        """Returns default paginator if action is not 'me'.

        :return: If action is 'me' - None, otherwise - superclass' paginator.
        """
        return None if self.action == "me" else super().paginator

    def get_queryset(self) -> QuerySet[User]:
        """Returns queryset of users with selected role.

        :return: Queryset of users with selected role.
        """
        return User.objects.all().select_related("role")

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Returns user by id, his username or email.

        :param request: Current request.
        :param args: Args
        :param kwargs: Kwargs.
        :return: Response with user.
        """
        key = kwargs.get("pk", "")
        with contextlib.suppress(ValueError):
            return super().retrieve(request, *args, pk=int(key))

        try:
            validate_email(key)
            user = self.get_queryset().filter(email=key).first()
        except ValidationError:
            user = get_object_or_404(self.get_queryset(), username=key)

        data = self.get_serializer(user).data if user else None
        return Response(data)

    @action(
        detail=False,
        methods=["GET"],
        name="user_me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Returns current user.

        :param request: Current request.
        :param args: Args.
        :param kwargs: Kwargs.
        :return: Response with current user.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class NotificationViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    """Set of notification views."""

    queryset = Notification.objects.all()
    permission_classes = [IsAdminOrNotificationDeletionByOwner]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.serializer_action_classes = {
            "list": auth_serializers.NotificationSerializer,
            "create": auth_serializers.NotificationBaseSerializer,
            "retrieve": auth_serializers.NotificationSerializer,
            "update": auth_serializers.NotificationBaseSerializer,
            "partial_update": auth_serializers.NotificationBaseSerializer,
        }

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Returns all user's notifications.

        :param request: Current request.
        :param args: Args.
        :param kwargs: Kwargs.
        :return: Response with notifications data.
        """
        user: User = get_object_or_404(
            User.objects.all().prefetch_related("notifications"),
            pk=kwargs.get("pk"),
        )
        serializer = self.get_serializer(user.notifications.all(), many=True)
        return Response(serializer.data)
