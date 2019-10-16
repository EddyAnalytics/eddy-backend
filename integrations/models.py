from django.db import models

from django_mysql.models import JSONField

integration_types = ['debezium']


def default():
    return {
        'host': 'debezium-connect',
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
