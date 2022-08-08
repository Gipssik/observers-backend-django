from rest_framework import views
from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from authentication.models import User
from authentication.permissions import CanChangeUserOrReadOnly
from authentication.serializers import (
    TokenObtainSerializer,
    UserSerializer,
    UserCreationSerializer,
    UserChangeSerializer,
)


class TokenObtainView(TokenObtainPairView):
    serializer_class = TokenObtainSerializer


class UserMeView(views.APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.is_anonymous:
            raise NotAuthenticated
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
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

    def get_serializer_class(self, *args, **kwargs):
        kwargs["partial"] = True
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_queryset(self):
        return User.objects.all().prefetch_related("role")

    def perform_create(self, serializer: UserCreationSerializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = UserSerializer(instance)
        return Response(instance_serializer.data)

    def perform_update(self, serializer: UserChangeSerializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        instance_serializer = UserSerializer(instance)

        return Response(instance_serializer.data)
