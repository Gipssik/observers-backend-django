from django.urls import include, path

urlpatterns = [
    path("", include("authentication.urls")),
    path("", include("forum.urls")),
    path("", include("news.urls")),
]
