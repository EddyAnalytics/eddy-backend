import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from debezium_connectors.models import DebeziumConnector, DebeziumConnectorConfig


class DebeziumConnectorNode(DjangoObjectType):
    class Meta:
        model = DebeziumConnector
        fields = '__all__'
        filter_fields = '__all__'
        interfaces = (graphene.relay.Node,)


class DebeziumConnectorConfigNode(DjangoObjectType):
    class Meta:
        model = DebeziumConnectorConfig
        fields = '__all__'
        filter_fields = '__all__'
        interfaces = (graphene.relay.Node,)


# Query

class Query(object):
    debezium_connector = graphene.Node.Field(DebeziumConnectorNode)
    all_debezium_connectors = DjangoFilterConnectionField(DebeziumConnectorNode)

    debezium_connector_config = graphene.Node.Field(DebeziumConnectorConfigNode)
    all_debezium_connector_configs = DjangoFilterConnectionField(DebeziumConnectorConfigNode)


# Mutation

class CreateDebeziumConnector(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        config_id = graphene.ID()

    debezium_connector = graphene.Field(DebeziumConnectorNode)

    def mutate(self, info, **kwargs):
        name = kwargs.get('name')
        config_id = kwargs.get('config_id')

        debezium_connector = DebeziumConnector()

        if name is not None:
            debezium_connector.name = name

        if config_id is not None:
            config = graphene.relay.Node.get_node_from_global_id(info, config_id)
            debezium_connector.config = config

        debezium_connector.save()
        return CreateDebeziumConnector(debezium_connector=debezium_connector)


class UpdateDebeziumConnector(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String()
        config_id = graphene.ID()

    debezium_connector = graphene.Field(DebeziumConnectorNode)

    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')
        config_id = kwargs.get('config_id')

        if id is None:
            return None

        debezium_connector = graphene.relay.Node.get_node_from_global_id(info, id)

        if debezium_connector is None:
            return None

        if name is not None:
            debezium_connector.name = name

        if config_id is not None:
            config = graphene.relay.Node.get_node_from_global_id(info, config_id)
            debezium_connector.config = config

        debezium_connector.save()
        return CreateDebeziumConnector(debezium_connector=debezium_connector)


class DeleteDebeziumConnector(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    debezium_connector = graphene.Field(DebeziumConnectorNode)

    def mutate(self, info, **kwargs):
        id = kwargs.get('id')

        if id is None:
            return None

        debezium_connector = graphene.relay.Node.get_node_from_global_id(info, id)

        if debezium_connector is None:
            return None

        debezium_connector.delete()
        return DeleteDebeziumConnector(debezium_connector=debezium_connector)


class CreateDebeziumConnectorConfig(graphene.Mutation):
    class Arguments:
        connector_class = graphene.String()
        tasks_max = graphene.Int()
        database_hostname = graphene.String()
        database_port = graphene.Int()
        database_user = graphene.String()
        database_password = graphene.String()
        database_server_id = graphene.Int()
        database_server_name = graphene.String()
        database_whitelist = graphene.String()
        database_history_kafka_bootstrap_servers = graphene.String()
        database_history_kafka_topic = graphene.String()
        connector_id = graphene.ID()

    debezium_connector_config = graphene.Field(DebeziumConnectorConfigNode)

    def mutate(self, info, **kwargs):
        connector_class = kwargs.get('connector_class')
        tasks_max = kwargs.get('tasks_max')
        database_hostname = kwargs.get('database_hostname')
        database_port = kwargs.get('database_port')
        database_user = kwargs.get('database_user')
        database_password = kwargs.get('database_password')
        database_server_id = kwargs.get('database_server_id')
        database_server_name = kwargs.get('database_server_name')
        database_whitelist = kwargs.get('database_whitelist')
        database_history_kafka_bootstrap_servers = kwargs.get('database_history_kafka_bootstrap_servers')
        database_history_kafka_topic = kwargs.get('database_history_kafka_topic')
        connector_id = kwargs.get('connector_id')

        debezium_connector_config = DebeziumConnectorConfig()

        if connector_class is not None:
            debezium_connector_config.connector_class = connector_class

        if tasks_max is not None:
            debezium_connector_config.tasks_max = tasks_max

        if database_hostname is not None:
            debezium_connector_config.database_hostname = database_hostname

        if database_port is not None:
            debezium_connector_config.database_port = database_port

        if database_user is not None:
            debezium_connector_config.database_user = database_user

        if database_password is not None:
            debezium_connector_config.database_password = database_password

        if database_server_id is not None:
            debezium_connector_config.database_server_id = database_server_id

        if database_server_name is not None:
            debezium_connector_config.database_server_name = database_server_name

        if database_whitelist is not None:
            debezium_connector_config.database_whitelist = database_whitelist

        if database_history_kafka_bootstrap_servers is not None:
            debezium_connector_config.database_history_kafka_bootstrap_servers = database_history_kafka_bootstrap_servers

        if database_history_kafka_topic is not None:
            debezium_connector_config.database_history_kafka_topic = database_history_kafka_topic

        if connector_id is not None:
            connector = graphene.relay.Node.get_node_from_global_id(info, connector_id)
            debezium_connector_config.connector = connector

        debezium_connector_config.save()
        return CreateDebeziumConnectorConfig(debezium_connector_config=debezium_connector_config)


class UpdateDebeziumConnectorConfig(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        connector_class = graphene.String()
        tasks_max = graphene.Int()
        database_hostname = graphene.String()
        database_port = graphene.Int()
        database_user = graphene.String()
        database_password = graphene.String()
        database_server_id = graphene.Int()
        database_server_name = graphene.String()
        database_whitelist = graphene.String()
        database_history_kafka_bootstrap_servers = graphene.String()
        database_history_kafka_topic = graphene.String()
        connector_id = graphene.ID()

    debezium_connector_config = graphene.Field(DebeziumConnectorConfigNode)

    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        connector_class = kwargs.get('connector_class')
        tasks_max = kwargs.get('tasks_max')
        database_hostname = kwargs.get('database_hostname')
        database_port = kwargs.get('database_port')
        database_user = kwargs.get('database_user')
        database_password = kwargs.get('database_password')
        database_server_id = kwargs.get('database_server_id')
        database_server_name = kwargs.get('database_server_name')
        database_whitelist = kwargs.get('database_whitelist')
        database_history_kafka_bootstrap_servers = kwargs.get('database_history_kafka_bootstrap_servers')
        database_history_kafka_topic = kwargs.get('database_history_kafka_topic')
        connector_id = kwargs.get('connector_id')

        if id is None:
            return None

        debezium_connector_config = graphene.relay.Node.get_node_from_global_id(info, id)

        if debezium_connector_config is None:
            return None

        if connector_class is not None:
            debezium_connector_config.connector_class = connector_class

        if tasks_max is not None:
            debezium_connector_config.tasks_max = tasks_max

        if database_hostname is not None:
            debezium_connector_config.database_hostname = database_hostname

        if database_port is not None:
            debezium_connector_config.database_port = database_port

        if database_user is not None:
            debezium_connector_config.database_user = database_user

        if database_password is not None:
            debezium_connector_config.database_password = database_password

        if database_server_id is not None:
            debezium_connector_config.database_server_id = database_server_id

        if database_server_name is not None:
            debezium_connector_config.database_server_name = database_server_name

        if database_whitelist is not None:
            debezium_connector_config.database_whitelist = database_whitelist

        if database_history_kafka_bootstrap_servers is not None:
            debezium_connector_config.database_history_kafka_bootstrap_servers = database_history_kafka_bootstrap_servers

        if database_history_kafka_topic is not None:
            debezium_connector_config.database_history_kafka_topic = database_history_kafka_topic

        if connector_id is not None:
            connector = graphene.relay.Node.get_node_from_global_id(info, connector_id)
            debezium_connector_config.connector = connector

        debezium_connector_config.save()
        return CreateDebeziumConnectorConfig(debezium_connector_config=debezium_connector_config)


class DeleteDebeziumConnectorConfig(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    debezium_connector_config = graphene.Field(DebeziumConnectorConfigNode)

    def mutate(self, info, **kwargs):
        id = kwargs.get('id')

        if id is None:
            return None

        debezium_connector_config = graphene.relay.Node.get_node_from_global_id(info, id)

        if debezium_connector_config is None:
            return None

        debezium_connector_config.delete()
        return DeleteDebeziumConnectorConfig(debezium_connector_config=debezium_connector_config)


class Mutation(object):
    create_debezium_connector = CreateDebeziumConnector.Field()
    update_debezium_connector = UpdateDebeziumConnector.Field()
    delete_debezium_connector = DeleteDebeziumConnector.Field()

    create_debezium_connector_config = CreateDebeziumConnectorConfig.Field()
    update_debezium_connector_config = UpdateDebeziumConnectorConfig.Field()
    delete_debezium_connector_config = DeleteDebeziumConnectorConfig.Field()
