from django.urls import path
from .views import UserView, DepartmentView, RoleView, FileUploadView


urlpatterns = [
    # User
    path(
        "users",
        UserView.as_view(
            {"get": "list", "post": "create"},
        ),
    ),
    path(
        "users/<int:id>",
        UserView.as_view(
            {"patch": "patch", "delete": "delete", "get": "retrieve"},
        ),
    ),
    path("users/search", UserView.as_view({"get": "search"}), name="search-user"),
    # Upload file user
    path(
        "users/upload-file",
        FileUploadView.as_view({"post": "post"}),
    ),
    # Department
    path(
        "departments",
        DepartmentView.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "departments/<int:id>",
        DepartmentView.as_view(
            {"get": "retrieve", "patch": "update", "delete": "destroy"}
        ),
    ),
    # Role
    path("roles", RoleView.as_view({"get": "list", "post": "create"})),
    path(
        "roles/<int:id>",
        RoleView.as_view({"get": "retrieve", "patch": "update", "delete": "destroy"}),
    ),
]
