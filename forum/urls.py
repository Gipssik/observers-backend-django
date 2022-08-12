from django.urls import path, include
from rest_framework.routers import DefaultRouter

from forum import views

router = DefaultRouter()
router.register(r"notifications", views.NotificationViewSet)
router.register(r"tags", views.TagViewSet),
router.register(r"questions", views.QuestionViewSet)
router.register(r"comments", views.CommentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
