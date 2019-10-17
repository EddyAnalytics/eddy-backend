import django.contrib.auth.models
from django.contrib import admin

from authentication.models import User
from utils.utils import ReadOnlyIdAdmin

admin.site.unregister(django.contrib.auth.models.User)
admin.site.unregister(django.contrib.auth.models.Group)
admin.site.register(User, ReadOnlyIdAdmin)
