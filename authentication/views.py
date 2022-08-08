from rest_framework import views, permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from authentication.models import User, Role
from authentication.permissions import CanChangeUserOrReadOnly
from authentication.serializers import (
    TokenObtainSerializer,
    UserSerializer,
    UserCreationSerializer,
    UserChangeSerializer,
    RoleSerializer,
    RoleBaseSerializer,
)
from common import mixins as common_mixins


class TokenObtainView(TokenObtainPairView):
    serializer_class = TokenObtainSerializer


class RoleViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "list": RoleSerializer,
            "create": RoleBaseSerializer,
            "retrieve": RoleSerializer,
            "update": RoleBaseSerializer,
            "partial_update": RoleBaseSerializer,
        }

    def get_queryset(self):
        return Role.objects.all().prefetch_related("users")


class UserViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    queryset = User.objects.all()
    permission_classes = [CanChangeUserOrReadOnly]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "list": UserSerializer,
            "create": UserCreationSerializer,
            "retrieve": UserSerializer,
            "update": UserChangeSerializer,
            "partial_update": UserChangeSerializer,
        }

    def get_queryset(self):
        return User.objects.all().select_related("role")


class UserMeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
