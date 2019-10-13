from django.contrib import admin

from integrations.models import IntegrationType, Integration

admin.site.register(IntegrationType)
admin.site.register(Integration)