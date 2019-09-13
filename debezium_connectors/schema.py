import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from debezium_connectors.models import DebeziumConnector, DebeziumConnectorConfig


class DebeziumConnectorNode(DjangoObjectType):
    class Meta:
        model = DebeziumConnector
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith']
        }
        interfaces = (graphene.relay.Node,)


class DebeziumConnectorConfigNode(DjangoObjectType):
    class Meta:
        model = DebeziumConnectorConfig
        filter_fields = {
            'database_hostname': ['exact', 'icontains', 'istartswith']
        }
        interfaces = (graphene.relay.Node,)


class Query(object):
    debezium_connector = graphene.Node.Field(DebeziumConnectorNode)
    all_debezium_connectors = DjangoFilterConnectionField(DebeziumConnectorNode)
    debezium_connector_config = graphene.Node.Field(DebeziumConnectorConfigNode)
    all_debezium_connector_configs = DjangoFilterConnectionField(DebeziumConnectorConfigNode)
