from django.urls import path
from .views import UserView, DepartmentView, RoleView, FileUploadView


urlpatterns = [
    # User
    path(
        "user/",
        UserView.as_view(
            {"get": "list", "post": "create"},
        ),
    ),
    path(
        "user/<int:id>/",
        UserView.as_view(
            {"patch": "patch", "delete": "delete", "get": "retrieve"},
        ),
    ),
    path("user/search/", UserView.as_view({"get": "search"}), name="search-user"),
    # Upload file user
    path(
        "user/upload-file/",
        FileUploadView.as_view({"post": "post"}),
    ),
    # Department
    path(
        "department/",
        DepartmentView.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "department/<int:id>/",
        DepartmentView.as_view(
            {"get": "retrieve", "patch": "update", "delete": "destroy"}
        ),
    ),
    # Role
    path("role/", RoleView.as_view({"get": "list", "post": "create"})),
    path(
        "role/<int:id>/",
        RoleView.as_view({"get": "retrieve", "patch": "update", "delete": "destroy"}),
    ),
]
