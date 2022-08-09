from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from authentication.models import User
from common import mixins as common_mixins
from forum.models import Notification
from forum.permissions import IsAdminOrNotificationDeletionByOwner
from forum.serializers import NotificationSerializer, NotificationBaseSerializer


class NotificationViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    queryset = Notification.objects.all()
    permission_classes = [IsAdminOrNotificationDeletionByOwner]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "list": NotificationSerializer,
            "create": NotificationBaseSerializer,
            "retrieve": NotificationSerializer,
            "update": NotificationBaseSerializer,
            "partial_update": NotificationBaseSerializer,
        }

    def retrieve(self, request, *args, **kwargs):
        """Returns all user's notifications."""

        u: User = get_object_or_404(
            User.objects.all().prefetch_related("notifications"), pk=kwargs.get("pk")
        )
        serializer = self.get_serializer(u.notifications.all(), many=True)
        return Response(serializer.data)
