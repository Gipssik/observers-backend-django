from django.urls import path, include

urlpatterns = [
    path("", include("authentication.urls")),
    path("", include("forum.urls")),
]
