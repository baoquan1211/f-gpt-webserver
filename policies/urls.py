from django.urls import path, include
from .views import PolicyView

urlpatterns = [
    path("", PolicyView.as_view({"post": "create", "get": "list"})),
    path("/<str:id>", PolicyView.as_view({"patch": "patch", "delete": "delete"})),
]
