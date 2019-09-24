from django.contrib import admin

# Register your models here.
from workspaces.models import Workspace, Project, Integration, IntegrationType

admin.site.register(Workspace)
admin.site.register(IntegrationType)
admin.site.register(Integration)
admin.site.register(Project)
