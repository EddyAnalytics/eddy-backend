from django_mysql.models import JSONField
from django.db import models


class Pipeline(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='pipelines', on_delete=models.CASCADE)
    project = models.ForeignKey('workspaces.Project', related_name='pipelines', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)


class Block(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='blocks', on_delete=models.CASCADE)
    pipeline = models.ForeignKey('pipelines.Pipeline', related_name='blocks', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    block_type = models.ForeignKey('pipelines.BlockType', related_name='blocks', on_delete=models.CASCADE)
    config = JSONField()


class BlockType(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=200)
    config = JSONField()
