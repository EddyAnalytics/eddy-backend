from django.db import models

# Create your models here.
from authentication.models import User
from workspaces.models import Project


class Pipeline(models.Model):
    requires_superuser = False
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='pipelines', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='pipelines', on_delete=models.CASCADE)


class BlockType(models.Model):
    requires_superuser = True
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='blocktypes', on_delete=models.CASCADE)


class Block(models.Model):
    requires_superuser = False
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='blocks', on_delete=models.CASCADE)
    block_type = models.ForeignKey(BlockType, related_name='blocks', on_delete=models.CASCADE)
    pipeline = models.ForeignKey(Pipeline, related_name='blocks', on_delete=models.CASCADE)
    json_config = models.CharField(max_length=200)
