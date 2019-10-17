from django.contrib import admin

from projects.models import DataConnectorType, DataConnector, Project

admin.site.register(Project)
admin.site.register(DataConnector)
admin.site.register(DataConnectorType)
