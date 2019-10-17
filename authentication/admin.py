from django.contrib import admin

from authentication.models import User
from utils.utils import ReadOnlyIdAdmin

admin.site.register(User, ReadOnlyIdAdmin)
