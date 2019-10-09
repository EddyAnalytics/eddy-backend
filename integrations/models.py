import json

import requests
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# examples: debezium, twitter, other data streams, external flink cluster, external hadoop cluster ...
# an integration specifies the configuration of a certain integration
# this integration can be external data or compute sources
from django_mysql.models import JSONField


class Integration(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', models.CASCADE, related_name='integrations')
    workspace = models.ForeignKey('workspaces.Workspace', related_name='integrations', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    integration_type = models.ForeignKey('integrations.IntegrationType', related_name='integrations',
                                         on_delete=models.CASCADE)
    config = JSONField()


class IntegrationType(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=200)
    config = JSONField()


class DebeziumConnector(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', models.CASCADE, related_name='debezium_connectors')
    name = models.CharField(max_length=200)
    config = models.OneToOneField('integrations.DebeziumConnectorConfig', models.CASCADE, related_name='connector')


@receiver(post_save, sender=DebeziumConnector)
def post_save_debezium_connector(signal, sender, instance: DebeziumConnector, using, **kwargs):
    connector = instance
    config = connector.config

    url = 'http://' + settings.DEBEZIUM_HOST + ':' + settings.DEBEZIUM_PORT + '/connectors/'

    headers = dict()
    headers['Accept'] = 'application/json'
    headers['Content-Type'] = 'application/json'

    config_dict = dict()
    config_dict['connector.class'] = config.connector_class
    config_dict['tasks.max'] = config.tasks_max
    config_dict['database.hostname'] = config.database_hostname
    config_dict['database.port'] = config.database_port
    config_dict['database.user'] = config.database_user
    config_dict['database.password'] = config.database_password
    config_dict['database.server.id'] = config.database_server_id
    config_dict['database.server.name'] = config.database_server_name
    config_dict['database.whitelist'] = config.database_whitelist
    config_dict['database.history.kafka.bootstrap.servers'] = config.database_history_kafka_bootstrap_servers
    config_dict['database.history.kafka.topic'] = config.database_history_kafka_topic

    connector_dict = dict()
    connector_dict['name'] = connector.name
    connector_dict['config'] = config_dict

    data = json.dumps(connector_dict)

    requests.post(url, headers=headers, data=data)


@receiver(post_delete, sender=DebeziumConnector)
def post_delete_debezium_connector(signal, sender, instance: DebeziumConnector, using, **kwargs):
    connector = instance

    url = 'http://' + settings.DEBEZIUM_HOST + ':' + settings.DEBEZIUM_PORT + '/connectors/' + connector.name + '/'

    headers = dict()
    headers['Accept'] = 'application/json'
    headers['Content-Type'] = 'application/json'

    requests.delete(url, headers=headers)


class DebeziumConnectorConfig(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', models.CASCADE, related_name='debezium_connector_configs')
    connector_class = models.CharField(max_length=200)
    tasks_max = models.IntegerField()
    database_hostname = models.CharField(max_length=200)
    database_port = models.IntegerField()
    database_user = models.CharField(max_length=200)
    database_password = models.CharField(max_length=200)
    database_server_id = models.IntegerField()
    database_server_name = models.CharField(max_length=200)
    database_whitelist = models.CharField(max_length=200)
    database_history_kafka_bootstrap_servers = models.CharField(max_length=200)
    database_history_kafka_topic = models.CharField(max_length=200)


@receiver(post_save, sender=DebeziumConnectorConfig)
def post_save_debezium_connector_config(signal, sender, instance: DebeziumConnectorConfig, using, **kwargs):
    config = instance
    if hasattr(config, 'connector'):
        connector = config.connector
        url = 'http://' + settings.DEBEZIUM_HOST + ':' + settings.DEBEZIUM_PORT + '/connectors/' + connector.name + '/config/'

        headers = dict()
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'

        config_dict = dict()
        config_dict['connector.class'] = config.connector_class
        config_dict['tasks.max'] = config.tasks_max
        config_dict['database.hostname'] = config.database_hostname
        config_dict['database.port'] = config.database_port
        config_dict['database.user'] = config.database_user
        config_dict['database.password'] = config.database_password
        config_dict['database.server.id'] = config.database_server_id
        config_dict['database.server.name'] = config.database_server_name
        config_dict['database.whitelist'] = config.database_whitelist
        config_dict['database.history.kafka.bootstrap.servers'] = config.database_history_kafka_bootstrap_servers
        config_dict['database.history.kafka.topic'] = config.database_history_kafka_topic

        data = json.dumps(config_dict)

        requests.put(url, headers=headers, data=data)
