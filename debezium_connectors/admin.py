from django.contrib import admin

# Register your models here.
from debezium_connectors.models import DebeziumConnector, DebeziumConnectorConfig

admin.site.register(DebeziumConnectorConfig)
admin.site.register(DebeziumConnector)
