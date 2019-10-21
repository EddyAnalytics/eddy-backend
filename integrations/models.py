import requests
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_mysql.models import JSONField

from utils.exceptions import ConflictException

integration_types = ['debezium']


def default():
    return {
        'host': 'my-connect-cluster-connect-api.strimzi-kafka-operator.svc.cluster.local',
        'port': '8083'
    }


# supports_data_connectors True --> Debezium (Twitter)
# support_data_connectors False --> (Spark Flink Hadoop)
class Integration(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', models.CASCADE, related_name='integrations')
    workspace = models.ForeignKey('workspaces.Workspace', related_name='integrations', on_delete=models.CASCADE)
    label = models.CharField(max_length=200, default='Debezium')
    integration_type = models.CharField(max_length=200, default='debezium')
    supports_data_connectors = models.BooleanField(default=False)
    config = JSONField(default=default)

    def __str__(self):
        return self.label


@receiver(post_save, sender=Integration)
def post_save_integration(signal, sender, instance: Integration, using, **kwargs):
    integration = instance
    if integration.integration_type == 'debezium':
        headers = dict()
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'
        url = 'http://' + integration.config['host'] + ':' + integration.config['port'] + '/connectors/'
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            raise ConflictException()
        if response.status_code != 200:
            raise ConflictException()
