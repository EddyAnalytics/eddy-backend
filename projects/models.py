import json
import logging

import requests
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_mysql.models import JSONField

import eddy_backend.celery

logger = logging.getLogger(__name__)


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='projects', on_delete=models.CASCADE)
    workspace = models.ForeignKey('workspaces.Workspace', related_name='projects', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label


def default():
    return {
        'type': 'mysql',
        'host': 'mysql.strimzi-kafka-operator.svc.cluster.local',
        'port': '3306',
        'user': 'root',
        'password': 'debezium',
        'databases': 'inventory'
    }


# examples: debezium, twitter, other data streams ...
# a data connector ingests from the integrated data stream and publishes to a topic specific for this data connector
# a block in the pipeline can read from this topic
class DataConnector(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='data_connectors', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', models.CASCADE, related_name='data_connectors')
    label = models.CharField(max_length=200)
    data_connector_type = models.ForeignKey('projects.DataConnectorType', models.CASCADE,
                                            related_name='data_connectors')
    config = JSONField(default=default)

    def __str__(self):
        return self.label


@receiver(post_save, sender=DataConnector)
def post_save_data_connector(signal, sender, instance: DataConnector, using, **kwargs):
    data_connector = instance
    data_connector_type = data_connector.data_connector_type
    if hasattr(data_connector_type,
               'integration') and data_connector_type.integration is not None and data_connector_type.integration.integration_type == 'debezium':
        integration = data_connector.data_connector_type.integration

        headers = dict()
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'

        unique_name = str(data_connector.project.id) + '.' + str(data_connector.id)
        unique_id = str(data_connector.id)

        connector_dict = dict()
        connector_dict['name'] = unique_name

        config_dict = dict()
        if data_connector.config['type'] == 'mysql':
            config_dict['connector.class'] = 'io.debezium.connector.mysql.MySqlConnector'
            config_dict['tasks.max'] = '1'
            config_dict['database.hostname'] = data_connector.config['host']
            config_dict['database.port'] = data_connector.config['port']
            config_dict['database.user'] = data_connector.config['user']
            config_dict['database.password'] = data_connector.config['password']
            config_dict['database.server.id'] = unique_id
            config_dict['database.server.name'] = unique_name
            config_dict['database.include.list'] = data_connector.config['databases']
            config_dict['database.history.kafka.topic'] = 'schema-changes' + '.' + unique_name
            config_dict['database.history.kafka.bootstrap.servers'] = settings.KAFKA_HOST + ':' + settings.KAFKA_PORT

        connector_dict['config'] = config_dict

        url = 'http://' + integration.config['host'] + ':' + integration.config['port'] \
              + '/connectors/'

        data = json.dumps(connector_dict)
        logger.debug(data)

        response = requests.post(url, headers=headers, data=data)
        logger.debug(response)
        logger.debug(response.content)
    elif data_connector_type.label == 'CSV':
        unique_name = str(data_connector.project.id) + '.' + str(data_connector.id)
        url = data_connector.config['url']
        topic = data_connector.config['topic']
        eddy_backend.celery.app.send_task('app.csv_to_kafka', (url, unique_name + '.' + topic))


@receiver(pre_delete, sender=DataConnector)
def pre_delete_data_connector(signal, sender, instance: DataConnector, using, **kwargs):
    data_connector = instance
    data_connector_type = data_connector.data_connector_type
    if hasattr(data_connector_type,
               'integration') and data_connector_type.integration is not None and data_connector_type.integration.integration_type == 'debezium':
        integration = data_connector.data_connector_type.integration

        headers = dict()
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'

        unique_name = str(data_connector.project.id) + '.' + str(data_connector.id)

        url = 'http://' + integration.config['host'] + ':' + integration.config['port'] + '/connectors/' + unique_name

        response = requests.delete(url, headers=headers)
        logger.debug(response)


class DataConnectorType(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=200, default='Debezium')
    integration = models.ForeignKey('integrations.Integration', models.CASCADE, related_name='data_connector_types',
                                    null=True, blank=True)
    config = JSONField(default=default)

    def __str__(self):
        return self.label
