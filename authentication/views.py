from typing import Any

from django.db.models import QuerySet
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from authentication import serializers as auth_serializers
from authentication.models import Role, User
from authentication.permissions import CanChangeUserOrReadOnly
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
