from django.contrib import admin
from users.models import User, Department, Role

admin.site.register(User)
admin.site.register(Department)
admin.site.register(Role)
