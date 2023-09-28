from django.urls import path, include
from .views import ConversationView
from rest_framework.routers import DefaultRouter


urlpattern = [
    path("", ConversationView.as_view({"get": "list"})),
    path("/admin", ConversationView.as_view({"get": "list_for_admin"})),
    path("/admin/<str:id>", ConversationView.as_view({"get": "get_for_admin"})),
    path(
        "/<str:id>",
        ConversationView.as_view({"get": "get", "patch": "patch", "delete": "delete"}),
    ),
    path(
        "/<str:id>/pdf-exporting",
        ConversationView.as_view({"get": "export_pdf"}),
    ),
]
