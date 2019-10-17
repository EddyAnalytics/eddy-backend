from django.contrib import admin

from integrations.models import Integration
from utils.utils import ReadOnlyIdAdmin

admin.site.register(Integration, ReadOnlyIdAdmin)
