from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.conf import settings

from users.models import User, Department, Role, FileUpload


class CustomObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = str(user.username)
        token["user_id"] = user.id
        token["is_admin"] = user.is_staff
        return token


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        # Add extra responses here
        data["username"] = self.user.username
        data["name"] = self.user.name
        data["user_id"] = self.user.id
        data["is_admin"] = self.user.is_staff
        return data


class FileSerializer(serializers.ModelSerializer):
    """Represents file upload serializer class."""

    class Meta:
        """Contains model & fields used by this serializer."""

        model = FileUpload
        fields = "__all__"
        read_only_fields = ("owner",)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Fields chỉ định thuộc tính sẽ serializer và trả về json
        # fields = "__all__"
        fields = (
            "id",
            "username",
            "email",
            "name",
            "password",
            "role_id",
            "department_id",
            "is_superuser",
            "is_active",
            "update_by",
            "create_at",
        )

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)

        print(password)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
