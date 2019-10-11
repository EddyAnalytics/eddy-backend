from django.core.management.base import BaseCommand

import projects.models


class Command(BaseCommand):
    help = 'Creates default Debezium data connector type'

    def handle(self, *args, **options):
        if len(projects.models.DataConnectorType.objects.all()) == 0:
            debezium_data_connector_type = projects.models.DataConnectorType()
            debezium_data_connector_type.label = 'Debezium'
            debezium_data_connector_type.schema = {
                'type': 'object',
                'properties': {
                    'type': {'type': 'string'},  # mysql
                    'host': {'type': 'string'},  # debezium-mysql
                    'port': {'type': 'string'},  # 3307
                    'user': {'type': 'string'},  # root
                    'password': {'type': 'string'}  # debezium
                }
            }
            debezium_data_connector_type.save()
            self.stdout.write('Debezium data connector type created')
        else:
            self.stdout.write('Debezium data connector type already exists')
