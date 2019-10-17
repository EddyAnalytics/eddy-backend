from django.contrib import admin

from utils.utils import ReadOnlyIdAdmin
from workspaces.models import Workspace

admin.site.register(Workspace, ReadOnlyIdAdmin)
