from django.urls import path, include
from rest_framework.routers import DefaultRouter

from forum.views import NotificationViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
