from django.db import models

# Create your models here.
from authentication.models import User


class Workspace(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='workspaces', on_delete=models.CASCADE)


class IntegrationType(models.Model):
    id = models.AutoField(primary_key=True)


class Integration(models.Model):
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, related_name='integrations', on_delete=models.CASCADE)
    integration_type = models.ForeignKey(IntegrationType, related_name='integrations', on_delete=models.CASCADE)


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, related_name='projects', on_delete=models.CASCADE)
