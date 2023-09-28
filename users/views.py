from rest_framework import status
from datetime import datetime
from django.utils import timezone
from rest_framework import viewsets
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

from .models import User, Department, Role
from users.serializers import (
    UserSerializer,
    DepartmentSerializer,
    RoleSerializer,
    TokenObtainPairSerializer,
)

# from .permissions import UserCustomPermission, Department_Role_CustomPermission
from users.paginations import CustomNumberPagination


class CustomTokenObtainPairView(TokenObtainPairView):
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
    dataframe["username"] = ""

    # Make column username
    for index, row in dataframe.iterrows():
        name_element = row["name_format"].split(" ")
        str_username = name_element[-1] + "-"

        for i in range(len(name_element) - 1):
            str_username += name_element[i][0]

        dataframe.at[index, "username"] = str_username
    # print(dataframe)

    # Group by and count username
    df_username = dataframe.groupby("username").size().reset_index(name="count")
    # print(df_username)

    # Count username exists in database
    for index, row in df_username.iterrows():
        count_username = User.objects.filter(username=row["username"]).aggregate(
            count=Count("username")
        )["count"]
        df_username.at[index, "count_db"] = int(count_username)

    # print(df_username)

    # Handle username must be unique
    for index_df, row_df in dataframe.iterrows():
        for index_user, row_user in df_username.iterrows():
            if row_df["username"] == row_user["username"]:
                if int(row_user["count_db"]) == 0:
                    # for i in range(int(row_user['count'])):
                    # if i == 0:
                    # break
                    # else:
                    # dataframe.at[index_df, 'username'] = row_df['username'] + str(i+1)
                    # break
                    dataframe.at[index_df, "username"] = row_df["username"]

                else:
                    # for i in range(int(row_user['count'])):
                    # dataframe.at[index_df, 'username'] = row_df['username'] + str(i + (int(row_user['count_db']) + 1))
                    dataframe.at[index_df, "username"] = row_df["username"] + str(
                        int(row_user["count_db"]) + 1
                    )

                # Update df_username
                df_username.at[index_user, "count"] = int(row_user["count"]) - 1
                df_username.at[index_user, "count_db"] = int(row_user["count_db"]) + 1

    # print(df_username)
    # print(dataframe)

    # Make list instance User
    user_data_list = []
    for index, row in dataframe.iterrows():
        # Create instance User
        user_data = User(
            username=row["username"],
            name=row["name"],
            email=row["email"],
            role_id=Role.objects.get(name=row["role"]),
            department_id=Department.objects.get(name=row["department"]),
            update_by=request.user,
        )
        # Hash password
        user_data.set_password("fujinet_system")

        # Append the instance User to the list
        user_data_list.append(user_data)
    return user_data_list


class FileUploadView(viewsets.ModelViewSet):
    """Represents file upload view class.

    API endpoint that allows users to upload a csv file.

    POST: upload file
    """

    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = UserSerializer

    def create(self, request, format=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
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

            # Read file by pandas
            if _csv is True:
                # Read csv file InMemoryUploadedFile
                data = file_obj.read().decode("UTF-8")
                # print(data)

                io_string = io.StringIO(data)
                user_df = pd.read_csv(io_string)
                # print(user_df)

                user_data_list = handle_dataframe(request, user_df)
                # print(user_data_list)

                if len(user_data_list) == 0:
                    return Response("File is empty", status=status.HTTP_400_BAD_REQUEST)

                # Create list instance User in one transaction
                User.objects.bulk_create(user_data_list)

                return Response("Upload successful", status=status.HTTP_201_CREATED)
            elif _excel is True:
                # Read xlsx file InMemoryUploadedFile
                user_df = pd.read_excel(file_obj)
                # print(user_df)

                user_data_list = handle_dataframe(request, user_df)
                # print(user_data_list)

                if len(user_data_list) == 0:
                    return Response("File is empty", status=status.HTTP_400_BAD_REQUEST)

                # Create list instance User in one transaction
                User.objects.bulk_create(user_data_list)

                return Response("Upload successful", status=status.HTTP_201_CREATED)
            else:
                return Response(
                    "Must be *.xlsx or *.csv File.", status=status.HTTP_400_BAD_REQUEST
                )
            # return Response("Upload successful", status=status.HTTP_201_CREATED)
        except Exception as ex:
            print(ex)
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)


class UserView(viewsets.ModelViewSet, BaseUserManager):
    # permission_classes = [UserCustomPermission]
    serializer_class = UserSerializer
    pagination_class = CustomNumberPagination

    def get_queryset(self):
        queryset = User.objects.select_related("department_id", "role_id").filter(
            delete_at=None
        )
        return queryset

    def list(self, request):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            # data = self.paginate_queryset(self.get_queryset())
            # user_serializer = UserSerializer(data, many=True)
            # users = user_serializer.data
            #
            # for i in range(len(users)):
            #     del users[i]['password']
            #
            #     if data[i].department_id is not None and data[i].role_id is not None and data[i].update_by is not None:
            #         users[i]['department_id'] = data[i].department_id.name
            #         users[i]['role_id'] = data[i].role_id.name
            #         users[i]['update_by'] = data[i].update_by.name
            #
            # # The pagination is handled automatically by CustomNumberPagination
            # return self.paginator.get_paginated_response(users)

            role = self.request.query_params.get("role", None)
            department = self.request.query_params.get("department", None)
            username = self.request.query_params.get("username", None)

            if role and department and username:
                queryset = self.get_queryset().filter(
                    role_id=role,
                    department_id=department,
                    username__startswith=username,
                )
            elif role and department:
                queryset = self.get_queryset().filter(
                    role_id=role, department_id=department
                )
            elif role and username:
                queryset = self.get_queryset().filter(
                    role_id=role, username__startswith=username
                )
            elif department and username:
                queryset = self.get_queryset().filter(
                    department_id=department, username__startswith=username
                )
            elif role:
                queryset = self.get_queryset().filter(role_id=role)
            elif department:
                queryset = self.get_queryset().filter(department_id=department)
            elif username:
                queryset = self.get_queryset().filter(username__startswith=username)
            else:
                queryset = self.get_queryset()

            data = self.paginate_queryset(queryset)

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

            # The pagination is handled automatically by CustomNumberPagination
            return self.paginator.get_paginated_response(users)

        except Exception as ex:
            print(ex)
            return Response(str(ex), status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, id=None):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            data = self.get_queryset().get(id=id)

            user_serializer = UserSerializer(data)
            user = user_serializer.data

            del user["password"]
            if (
                data.department_id is not None
                and data.role_id is not None
                and data.update_by is not None
            ):
                user["department_id"] = data.department_id.name
                user["role_id"] = data.role_id.name
                user["update_by"] = data.update_by.name

            return Response(user, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            data = request.data
            user_serializer = UserSerializer(data=data)

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
            user_request = self.request.user
            user = User.objects.get(id=id)
            if user is None:
                return Response("User is not valid", status=status.HTTP_404_NOT_FOUND)
            # Name
            new_name = request.data.get("name", "")
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

            # User update
            user.update_by = user_request

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
            user_request = self.request.user
            user = User.objects.get(id=id)

            if user is None:
                return Response("User is not valid", status=status.HTTP_404_NOT_FOUND)
            user.delete_at = timezone.now()
            user.update_by = user_request

            user.save()
            return Response("Delete user success", status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    def search(self, request):
        """
        Search user by username and startswith
        """
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            # Get query params
            role = self.request.query_params.get("role", None)
            department = self.request.query_params.get("department", None)
            username = self.request.query_params.get("username", None)

            print(role)
            print(department)
            print(username)

            if role and department and username:
                data = User.objects.filter(
                    role_id=role,
                    department_id=department,
                    username__startswith=username,
                    delete_at=None,
                )
            elif role and department:
                data = User.objects.filter(
                    role_id=role, department_id=department, delete_at=None
                )
            elif role and username:
                data = User.objects.filter(
                    role_id=role, username__startswith=username, delete_at=None
                )
            elif department and username:
                data = User.objects.filter(
                    department_id=department,
                    username__startswith=username,
                    delete_at=None,
                )
            elif role:
                data = User.objects.filter(role_id=role, delete_at=None)
            elif department:
                data = User.objects.filter(department_id=department, delete_at=None)
            elif username:
                data = User.objects.filter(
                    username__startswith=username, delete_at=None
                )
            else:
                data = User.objects.all(delete_at=None)

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

            return Response(users, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    def filter(self, request):
        """
        Filter user by role_id and department_id
        """
        if request is None:
            return Response("Response is not valid", status=status.HTTP_400_BAD_REQUEST)
        try:
            role = self.request.query_params.get("role", None)
            department = self.request.query_params.get("department", None)
            username = self.request.query_params.get("username", None)

            if role and department and username:
                data = User.objects.filter(
                    role_id=role,
                    department_id=department,
                    username__startswith=username,
                    delete_at=None,
                )
            elif role and department:
                data = User.objects.filter(
                    role_id=role, department_id=department, delete_at=None
                )
            elif role and username:
                data = User.objects.filter(
                    role_id=role, username__startswith=username, delete_at=None
                )
            elif department and username:
                data = User.objects.filter(
                    department_id=department,
                    username__startswith=username,
                    delete_at=None,
                )
            elif role:
                data = User.objects.filter(role_id=role, delete_at=None)
            elif department:
                data = User.objects.filter(department_id=department, delete_at=None)
            elif username:
                data = User.objects.filter(
                    username__startswith=username, delete_at=None
                )
            else:
                data = User.objects.all(delete_at=None)

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

            return Response(users, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)


class DepartmentView(viewsets.ModelViewSet):
    # permission_classes = [Department_Role_CustomPermission]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

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

    def patch(self, request, id=None):
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

    def delete(self, request, id=None):
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


class RoleView(viewsets.ModelViewSet):
    # permission_classes = [Department_Role_CustomPermission]
    # permission_classes = [permissions.IsAdminUser]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

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

    def patch(self, request, id=None):
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

    def delete(self, request, id=None):
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
