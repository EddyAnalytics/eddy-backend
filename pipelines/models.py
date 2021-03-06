from django.db import models
from django_mysql.models import JSONField


class Pipeline(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='pipelines', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', related_name='pipelines', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    config = JSONField()

    def __str__(self):
        return self.label


class Block(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='blocks', on_delete=models.CASCADE)
    pipeline = models.ForeignKey('pipelines.Pipeline', related_name='blocks', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    block_type = models.ForeignKey('pipelines.BlockType', related_name='blocks', on_delete=models.CASCADE)
    config = JSONField()

    def __str__(self):
        return self.label


class BlockType(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=200)
    config = JSONField()

    def __str__(self):
        return self.label
