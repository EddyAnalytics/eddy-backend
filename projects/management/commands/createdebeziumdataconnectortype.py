from django.core.management.base import BaseCommand

import projects.models


class Command(BaseCommand):
    help = 'Creates default Debezium data connector type'

    def handle(self, *args, **options):
        if len(projects.models.DataConnectorType.objects.all()) == 0:
            debezium_data_connector_type = projects.models.DataConnectorType()
            debezium_data_connector_type.label = 'Debezium'
            debezium_data_connector_type.config = {'type': 'mysql',
                                                   'hostname': 'debezium-mysql',
                                                   'port': 3307,
                                                   'user': 'root',
                                                   'password': 'debezium'}
            debezium_data_connector_type.save()
            self.stdout.write('Debezium data connector type created')
        else:
            self.stdout.write('Debezium data connector type already exists')
