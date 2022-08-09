from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authentication import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"roles", views.RoleViewSet)

urlpatterns = [
    path("token/", views.TokenObtainView.as_view(), name="token_obtain"),
    path("users/me/", views.UserMeView.as_view(), name="user_me"),
    path("", include(router.urls)),
]
