from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings



class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, username, name, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")

        return self.create_user(email, username, name, password, **other_fields)

    def create_user(self, email, username, name, password, **other_fields):
        if not email:
            raise ValueError(_("You must provide an email address"))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, name=name, **other_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(max_length=150, blank=True)
    role_id = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    department_id = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    create_at = models.DateTimeField(default=timezone.now, editable=False)
    update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    update_at = models.DateTimeField(auto_now=True, editable=False)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    last_login = models.DateTimeField(
        _("last login"), blank=True, null=True, editable=False
    )

    objects = CustomAccountManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "name"]

    def __str__(self):
        return self.username


def upload_to(instance, filename):
    return "users/{filename}".format(filename=filename)


class FileUpload(models.Model):
    """Represents file upload model class."""

    owner = models.CharField(max_length=250)
    file = models.FileField(_("File"), upload_to=upload_to)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return file name."""
        return self.file.name
