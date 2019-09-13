import graphene
from graphene_django.types import DjangoObjectType

from debezium_connectors.models import DebeziumConnector, DebeziumConnectorConfig


class DebeziumConnectorType(DjangoObjectType):
    class Meta:
        model = DebeziumConnector


class DebeziumConnectorConfigType(DjangoObjectType):
    class Meta:
        model = DebeziumConnectorConfig


class Query(object):
    debezium_connector = graphene.Field(DebeziumConnectorType, id=graphene.Int())
    all_debezium_connectors = graphene.List(DebeziumConnectorType)
    debezium_connector_config = graphene.Field(DebeziumConnectorConfigType, id=graphene.Int())
    all_debezium_connector_configs = graphene.List(DebeziumConnectorConfigType)

    def resolve_debezium_connector(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return DebeziumConnector.objects.get(pk=id)
        return None

    def resolve_all_debezium_connectors(self, info, **kwargs):
        return DebeziumConnector.objects.all()

    def resolve_debezium_connector_config(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return DebeziumConnectorConfig.objects.get(pk=id)
        return None

    def resolve_debezium_connector_configs(self, info, **kwargs):
        # We can easily optimize query count in the resolve method
        return DebeziumConnectorConfig.objects.all()
