from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from authentication.models import User, Role
from authentication.permissions import CanChangeUserOrReadOnly
from authentication import serializers as auth_serializers
from common import mixins as common_mixins


class TokenObtainView(TokenObtainPairView):
    serializer_class = auth_serializers.TokenObtainSerializer


class RoleViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    queryset = Role.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "list": auth_serializers.RoleSerializer,
            "create": auth_serializers.RoleBaseSerializer,
            "retrieve": auth_serializers.RoleSerializer,
            "update": auth_serializers.RoleBaseSerializer,
            "partial_update": auth_serializers.RoleBaseSerializer,
        }

    def get_queryset(self):
        return Role.objects.all().prefetch_related("users")


class UserViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    queryset = User.objects.all()
    permission_classes = [CanChangeUserOrReadOnly]

    @property
    def paginator(self):
        return None if self.action == "me" else super().paginator

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "list": auth_serializers.UserSerializer,
            "create": auth_serializers.UserCreationSerializer,
            "retrieve": auth_serializers.UserSerializer,
            "update": auth_serializers.UserChangeSerializer,
            "partial_update": auth_serializers.UserChangeSerializer,
            "me": auth_serializers.UserSerializer,
        }

    def get_queryset(self):
        return User.objects.all().select_related("role")

    @action(
        detail=False,
        methods=["GET"],
        name="user_me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        serializer = auth_serializers.UserSerializer(request.user)
        return Response(serializer.data)
