from django.urls import include, path
from rest_framework.routers import DefaultRouter

from news import views

router = DefaultRouter()
router.register("articles", views.ArticleViewSet)

urlpatterns = [
    path("news/", include(router.urls)),
]
