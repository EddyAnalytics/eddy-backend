from django.db import models

from django_mysql.models import JSONField


# examples: debezium, twitter, other data streams, external flink cluster, external hadoop cluster ...
# an integration specifies the configuration of a certain integration
# this integration can be external data or compute sources
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
    schema = JSONField()
