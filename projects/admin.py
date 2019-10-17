from django.contrib import admin

from projects.models import DataConnectorType, DataConnector, Project
from utils.utils import ReadOnlyIdAdmin

admin.site.register(Project, ReadOnlyIdAdmin)
admin.site.register(DataConnector, ReadOnlyIdAdmin)
admin.site.register(DataConnectorType, ReadOnlyIdAdmin)
