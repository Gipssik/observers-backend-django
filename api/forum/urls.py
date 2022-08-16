from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.forum import views

router = DefaultRouter()
router.register("tags", views.TagViewSet)
router.register("questions", views.QuestionViewSet)
router.register("comments", views.CommentViewSet)

urlpatterns = [
    path("forum/", include(router.urls)),
]
