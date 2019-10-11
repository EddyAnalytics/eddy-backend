from django.core.management.base import BaseCommand

import integrations.models


class Command(BaseCommand):
    help = 'Creates default Debezium integration type'

    def handle(self, *args, **options):
        if len(integrations.models.IntegrationType.objects.all()) == 0:
            debezium_integration_type = integrations.models.IntegrationType()
            debezium_integration_type.label = 'Debezium'
            debezium_integration_type.schema = {
                'type': 'object',
                'properties': {
                    'host': {"type": 'string'},  # 'debezium-connect'
                    'port': {"type": 'string'},  # '8083'
                }
            }
            debezium_integration_type.save()
            self.stdout.write('Debezium integration type created')
        else:
            self.stdout.write('Debezium integration type already exists')
