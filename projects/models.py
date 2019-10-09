from django.db import models
from django_mysql.models import JSONField


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='projects', on_delete=models.CASCADE)
    workspace = models.ForeignKey('workspaces.Workspace', related_name='projects', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)


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
    config = JSONField()
    #  TODO topics field


class DataConnectorType(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=200)
    config = JSONField()

# TODO auto add debezium connector data connector type