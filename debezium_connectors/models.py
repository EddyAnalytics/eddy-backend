from django.db import models


# Create your models here.
class DebeziumConnectorConfig(models.Model):
    id = models.AutoField(primary_key=True)
    connector_class = models.CharField(default='io.debezium.connector.mysql.MySqlConnector', max_length=200)
    tasks_max = models.IntegerField(default=1)
    database_hostname = models.CharField(default='mysql', max_length=200)
    database_port = models.IntegerField(default=3306)
    database_user = models.CharField(default='root', max_length=200)
    database_password = models.CharField(default='debezium', max_length=200)
    database_server_id = models.IntegerField(default='184054')
    database_server_name = models.CharField(default='mysql1', max_length=200)
    database_whitelist = models.CharField(default='inventory', max_length=200)
    database_history_kafka_bootstrap_servers = models.CharField(default='kafka:9092', max_length=200)
    database_history_kafka_topic = models.CharField(default='schema-changes.inventory', max_length=200)

    def __str__(self):
        try:
            return self.connector.name + ' ' + 'config'
        except DebeziumConnector.DoesNotExist:
            return 'config'


class DebeziumConnector(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(default='inventory-connector', max_length=200)
    config = models.OneToOneField(DebeziumConnectorConfig, related_name='connector', blank=True, null=True,
                                  on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
