from django.urls import include, path
from rest_framework.routers import DefaultRouter

from authentication import views

router = DefaultRouter()
router.register("users", views.UserViewSet)
router.register("roles", views.RoleViewSet)
router.register("notifications", views.NotificationViewSet)

urlpatterns = [
    path("token/", views.TokenObtainView.as_view(), name="token_obtain"),
    path("accounts/", include(router.urls)),
]
