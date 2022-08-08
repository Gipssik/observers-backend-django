from django.urls import path, include
from rest_framework import routers

from authentication.views import UserViewSet, TokenObtainView, UserMeView, RoleViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"roles", RoleViewSet)

urlpatterns = [
    path("token/", TokenObtainView.as_view(), name="token_obtain"),
    path("users/me/", UserMeView.as_view(), name="user_me"),
    path("", include(router.urls)),
]
