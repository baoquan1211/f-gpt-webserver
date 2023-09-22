from django.urls import path, include
from .views import ConversationView
from rest_framework.routers import DefaultRouter


urlpattern = [
    path("", ConversationView.as_view({"get": "list"})),
    path(
        "/<str:id>",
        ConversationView.as_view({"get": "get"}),
    ),
    path(
        "/<str:id>",
        ConversationView.as_view({"patch": "patch"}),
    ),
    path(
        "/<str:id>",
        ConversationView.as_view({"delete": "delete"}),
    ),
    path(
        "/<str:id>/pdf-exporting",
        ConversationView.as_view({"get": "export_pdf"}),
    ),
]
