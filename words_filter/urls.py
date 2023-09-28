from django.urls import path
from words_filter.views import BlockedMessageView

urlpatterns = [
    path("", BlockedMessageView.as_view({"get": "list"})),
    path("/<str:id>", BlockedMessageView.as_view({"get": "get"})),
]
