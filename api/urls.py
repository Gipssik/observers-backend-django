from django.urls import include, path

urlpatterns = [
    path("", include("api.authentication.urls")),
    path("", include("api.forum.urls")),
    path("", include("api.news.urls")),
]
