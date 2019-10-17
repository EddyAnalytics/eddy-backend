import django.contrib.auth.models
from django.contrib import admin

from authentication.models import User
from utils.utils import ReadOnlyIdAdmin


class ReadOnlyIdUserAdmin(ReadOnlyIdAdmin):
    exclude = ('last_login', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'groups',
               'user_permisisons')


admin.site.unregister(django.contrib.auth.models.User)
admin.site.unregister(django.contrib.auth.models.Group)
admin.site.register(User, ReadOnlyIdUserAdmin)
