from django.core.management.base import BaseCommand

import integrations.models


class Command(BaseCommand):
    help = 'Creates default Debezium integration type'

    def handle(self, *args, **options):
        if len(integrations.models.IntegrationType.objects.all()) == 0:
            debezium_integration_type = integrations.models.IntegrationType()
            debezium_integration_type.label = 'Debezium'
            debezium_integration_type.config = {
                'host': 'debezium-connect',
                'port': '8083'
            }
            debezium_integration_type.save()
            self.stdout.write('Debezium integration type created')
        else:
            self.stdout.write('Debezium integration type already exists')
