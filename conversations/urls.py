from django.urls import path, include
from .views import ConversationView
from rest_framework.routers import DefaultRouter


urlpattern = [
    path("", ConversationView.as_view({"get": "list"}), name="get_all"),
    path(
        "<str:id>/",
        ConversationView.as_view({"get": "get"}),
        name="get_by_id",
    ),
    path(
        "<str:id>/",
        ConversationView.as_view({"patch": "patch"}),
        name="patch_name",
    ),
    path(
        "<str:id>/",
        ConversationView.as_view({"delete": "delete"}),
        name="delete",
    ),
]
