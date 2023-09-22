from rest_framework import status
from datetime import datetime
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import filters
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import BaseUserManager
from django.forms.models import model_to_dict
import pandas as pd
import io
from unidecode import unidecode
from django.db.models import Count
from users.models import User, Department, Role
from users.serializers import (
    UserSerializer,
    DepartmentSerializer,
    RoleSerializer,
    TokenObtainPairSerializer,
    FileSerializer,
)


class UserCustomPermission(permissions.BasePermission):
    """
    User only read (better only read information myself).

    Admin can read, edit all information user
    """

    message = "User only read (better only read information myself). Admin can read, edit all information user"

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        else:
            if request.methods in permissions.SAFE_METHODS:
                # Read only information yourself
                return obj.id == request.user
            else:
                # Write only information yourself
                return obj.id == request.user


class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


def handle_dataframe(request, dataframe):
    """Represents handle file upload view class.

    Input: dataframe
    Output: List users after handle

    """
    # Get columns and check column name ['name', 'email', 'role', 'department']
    columns = dataframe.columns.values
    list_column = ["name", "email", "role", "department"]

    for col in list_column:
        if col not in columns:
            return Response(
                "File must include all 4 columns ['name','email','role','department'] and columns "
                "name must be correct format",
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Count null value attribute name
    count_name_null = dataframe["name"].isnull().sum()
    if count_name_null > 0:
        return Response(
            "Exists value is null. Check!", status=status.HTTP_400_BAD_REQUEST
        )

    dataframe["name_format"] = dataframe["name"].str.lower().apply(unidecode)
    # Make username and user list
    user_data_list = []

    for index, row in dataframe.iterrows():
        name_element = row["name_format"].split(" ")
        # print(name_element)
        str_username = name_element[-1] + "-"

        for i in range(len(name_element) - 1):
            str_username += name_element[i][0]
        # print(str_username)

        # Count username in your database
        count_username = User.objects.filter(username=str_username).aggregate(
            count=Count("username")
        )["count"]
        # print(count_username)

        if count_username > 0:
            str_username += str(count_username + 1)
        # print(str_username)

        # Create a dictionary for the current user
        user_data = {
            "username": str_username,
            "name": row["name"],
            "email": row["email"],
            "password": "fujinet_system",
            "role_id": Role.objects.get(name=row["role"]).id,
            "department_id": Department.objects.get(name=row["department"]).id,
            "update_by": request.user.id,
        }

        # # Append the user data dictionary to the list
        user_data_list.append(user_data)

    return user_data_list


class FileUploadView(viewsets.ViewSet):
    """Represents file upload view class.

    API endpoint that allows users to be upload a csv file.

    POST: upload file
    """

    permission_classes = [permissions.IsAuthenticated, UserCustomPermission]
    parser_classes = [MultiPartParser, FormParser]
    # serializer_class = FileSerializer

    def post(self, request, format=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            request.data["owner"] = request.user.id
            file_serializer = FileSerializer(data=request.data)

            # Check file is csv or xlsx
            _dict_file_obj = request.data["file"].__dict__
            # print(_dict_file_obj)
            _csv = _dict_file_obj["_name"].endswith(".csv")
            _excel = _dict_file_obj["_name"].endswith(".xlsx")

            # Check file exists
            if request.FILES["file"] is None:
                return Response(
                    {"error": "No File Found"}, status=status.HTTP_400_BAD_REQUEST
                )
            # Get file
            file_obj = request.FILES["file"]

            if file_serializer.is_valid():
                owner_id = request.user.id
                file_serializer.validated_data["owner"] = owner_id

                # Read file by pandas
                if _csv is True:
                    # Read csv file InMemoryUploadedFile
                    data = file_obj.read().decode("UTF-8")
                    io_string = io.StringIO(data)

                    user_df = pd.read_csv(io_string)
                    # print(user_df)

                    user_data_list = handle_dataframe(request, user_df)

                    if len(user_data_list) == 0:
                        return Response(
                            "File is empty", status=status.HTTP_400_BAD_REQUEST
                        )

                    # Serializer user
                    users_serializer = UserSerializer(data=user_data_list, many=True)

                    if users_serializer.is_valid():
                        file_serializer.save()
                        users = users_serializer.save()

                        if users:
                            return Response(
                                {
                                    "message": "Upload successful",
                                    "data": file_serializer.data,
                                },
                                status=status.HTTP_201_CREATED,
                            )
                    return Response(
                        users_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

                elif _excel is True:
                    # Read xlsx file InMemoryUploadedFile
                    user_df = pd.read_excel(file_obj)
                    # print(user_df)

                    user_data_list = handle_dataframe(request, user_df)

                    if len(user_data_list) == 0:
                        return Response(
                            "File is empty", status=status.HTTP_400_BAD_REQUEST
                        )

                    # Serializer user
                    users_serializer = UserSerializer(data=user_data_list, many=True)

                    if users_serializer.is_valid():
                        users = users_serializer.save()
                        file_serializer.save()
                        if users:
                            return Response(
                                {
                                    "message": "Upload successful",
                                    "data": file_serializer.data,
                                },
                                status=status.HTTP_201_CREATED,
                            )
                    return Response(
                        users_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

                else:
                    return Response(
                        "Must be *.xlsx or *.csv File.",
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response("Upload successful", status=status.HTTP_201_CREATED)
        except Exception as ex:
            print(ex)
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)


class UserView(viewsets.ViewSet, BaseUserManager):
    permission_classes = [permissions.IsAuthenticated, UserCustomPermission]
    # serializer_class = UserSerializer
    # queryset = User.objects.all()

    def list(self, request):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            data = User.objects.select_related("department_id", "role_id").filter(
                delete_at=None
            )

            # print(data[0])
            # print(type(data[0].department_id))
            # print((data[0].department_id).name)

            user_serializer = UserSerializer(data, many=True)
            users = user_serializer.data

            for i in range(len(users)):
                del users[i]["password"]

                if (
                    data[i].department_id is not None
                    and data[i].role_id is not None
                    and data[i].update_by is not None
                ):
                    users[i]["department_id"] = data[i].department_id.name
                    users[i]["role_id"] = data[i].role_id.name
                    users[i]["update_by"] = data[i].update_by.name

            if users:
                return Response(users, status=status.HTTP_200_OK)
            else:
                return Response("Users is not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, id=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            data = User.objects.select_related("department_id", "role_id").get(
                id=id, delete_at=None
            )
            # print(type(data.department_id))

            user_serializer = UserSerializer(data)
            user = user_serializer.data
            # print(user)
            del user["password"]

            if (
                data.department_id is not None
                and data.role_id is not None
                and data.update_by is not None
            ):
                user["department_id"] = data.department_id.name
                user["role_id"] = data.role_id.name
                user["update_by"] = data.update_by.name
            # print(user)
            # user['department_id'] = Department.objects.get(id=user['department_id']).name
            # user['role_id'] = Role.objects.get(id=user['role_id']).name

            return Response(user, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            user_serializer = UserSerializer(data=request.data)

            if user_serializer.is_valid():
                user = user_serializer.save()
                if user:
                    return Response(status=status.HTTP_201_CREATED)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=id)
            # Name
            new_name = request.data.get("name", "")
            print(new_name)
            if new_name != "":
                user.name = new_name
            # Role
            new_role = request.data.get("role_id", "")
            if new_role != "":
                user.role_id = Role.objects.get(id=new_role)
            # Department
            new_department = request.data.get("department_id", "")
            if new_department != "":
                user.department_id = Department.objects.get(id=new_department)
            # Active
            new_active = request.data.get("is_active", "")
            if new_active != "":
                user.is_active = new_active

            new_password = request.data.get("password", "")
            if new_password != "":
                user.set_password(new_password)

            user_serializer = UserSerializer(user, data=model_to_dict(user))

            if user_serializer.is_valid():
                user_serializer.save()
                return Response(user_serializer.data, status=status.HTTP_200_OK)

            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id=None):
        if request is None:
            return Response("Request is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=id)
            if user is None:
                return Response("User is not valid", status=status.HTTP_404_NOT_FOUND)
            user.delete_at = datetime.now()
            user.save()
            return Response("Delete user success", status=status.HTTP_200_OK)
            # return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    def search(self, request):
        """
        Search user by username and startswith
        """
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            # Use square brackets to access query parameters
            username = self.request.query_params.get("username", None)
            # print(username)

            data = User.objects.filter(username__startswith=username)
            # print(data)

            user_serializer = UserSerializer(data, many=True)

            users = user_serializer.data

            for i in range(len(users)):
                del users[i]["password"]

                if (
                    data[i].department_id is not None
                    and data[i].role_id is not None
                    and data[i].update_by is not None
                ):
                    users[i]["department_id"] = data[i].department_id.name
                    users[i]["role_id"] = data[i].role_id.name
                    users[i]["update_by"] = data[i].update_by.name

            if users:
                return Response(users, status=status.HTTP_200_OK)
            else:
                return Response("Users is not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)


# Hướng filter backend không ổn
# class SearchUser(viewsets.ModelViewSet):
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAdminUser]
#
#     # Search filter backend
#     # '^' Starts-with search
#     filter_backends = [filters.SearchFilter]
#     search_fields = ["^username"]
#
#     def get_queryset(self):
#         queryset = User.objects.select_related('department_id', 'role_id').filter(delete_at=None)
#         return queryset
#
#     def search(self, request):
#         if request is None:
#             return Response(
#                 "Response is not valid", status=status.HTTP_400_BAD_REQUEST
#             )
#         try:
#             data = self.filter_queryset(self.get_queryset())
#             print(data)
#
#             user_serializer = UserSerializer(
#                 data, many=True
#             )
#
#             users = user_serializer.data
#
#             for i in range(len(users)):
#                 del users[i]['password']
#
#                 if data[i].department_id is not None and data[i].role_id is not None and data[i].update_by is not None:
#                     users[i]['department_id'] = data[i].department_id.name
#                     users[i]['role_id'] = data[i].role_id.name
#                     users[i]['update_by'] = data[i].update_by.name
#
#             if users:
#                 return Response(users, status=status.HTTP_200_OK)
#             else:
#                 return Response('Users is not found', status=status.HTTP_404_NOT_FOUND)
#         except Exception as ex:
#             print(ex)
#             return Response(
#                 str(ex), status=status.HTTP_400_BAD_REQUEST
#             )


class DepartmentView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    # queryset = Department.objects.all()
    # serializer_class = DepartmentSerializer

    def list(self, request):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            department_serializer = DepartmentSerializer(self.queryset, many=True)
            users = department_serializer.data

            if users:
                return Response(users, status=status.HTTP_200_OK)
            else:
                return Response(
                    "Departments is not found", status=status.HTTP_404_NOT_FOUND
                )
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, id=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            department_serializer = DepartmentSerializer(Department.objects.get(id=id))
            department = department_serializer.data
            return Response(department, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            data = request.data
            department_serializer = DepartmentSerializer(data=data)

            if department_serializer.is_valid():
                department = department_serializer.save()
                if department:
                    return Response(
                        department_serializer.data, status=status.HTTP_201_CREATED
                    )
            return Response(
                department_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_404_NOT_FOUND)

    def update(self, request, id=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            department = Department.objects.get(id=id)
            print(department)
            print(type(department))
            new_name = request.data.get("name", "")
            print(new_name)

            if new_name == "":
                return Response(
                    "New name department is empty", status=status.HTTP_400_BAD_REQUEST
                )

            # Carefully
            # .save() will create a new instance.
            # serializer = CommentSerializer(data=data)

            # .save() will update the existing `comment` instance.
            # serializer = CommentSerializer(comment, data=data)
            department.name = new_name
            department_serializer = DepartmentSerializer(
                department, data=model_to_dict(department)
            )

            if department_serializer.is_valid():
                department_serializer.save()
                return Response(department_serializer.data, status=status.HTTP_200_OK)
            return Response(
                department_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            department = Department.objects.get(id=id)

            if department is None:
                return Response(
                    "Department is not found", status=status.HTTP_404_NOT_FOUND
                )

            department.delete()
            return Response("Delete department successful", status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)


class RoleView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    # queryset = Role.objects.all()
    # serializer_class = RoleSerializer

    def list(self, request):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            role_serializer = RoleSerializer(self.queryset, many=True)
            roles = role_serializer.data

            if roles:
                return Response(roles, status=status.HTTP_200_OK)
            else:
                return Response("Roles is not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, id=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            role_serializer = RoleSerializer(Role.objects.get(id=id))
            role = role_serializer.data
            return Response(role, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            data = request.data
            role_serializer = RoleSerializer(data=data)

            if role_serializer.is_valid():
                department = role_serializer.save()
                if department:
                    return Response(
                        role_serializer.data, status=status.HTTP_201_CREATED
                    )
            return Response(role_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_404_NOT_FOUND)

    def update(self, request, id=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            role = Role.objects.get(id=id)
            # print(role)
            # print(type(role))

            new_name = request.data.get("name", "")
            # print(new_name)

            if new_name == "":
                return Response(
                    "New department name is empty", status=status.HTTP_400_BAD_REQUEST
                )
            role.name = new_name
            role_serializer = RoleSerializer(role, data=model_to_dict(role))

            if role_serializer.is_valid():
                role_serializer.save()
                return Response(role_serializer.data, status=status.HTTP_200_OK)
            return Response(role_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            role = Role.objects.get(id=id)

            if role is None:
                return Response("Role is not found", status=status.HTTP_404_NOT_FOUND)
            print(role)
            role.delete()
            return Response("Delete role successful", status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
