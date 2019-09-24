from django.db import models

# Create your models here.
from authentication.models import User


class Workspace(models.Model):
    user = models.ForeignKey(User, related_name='workspaces', on_delete=models.CASCADE)
    pass


class IntegrationType(models.Model):
    pass


class Integration(models.Model):
    workspace = models.ForeignKey(Workspace, related_name='integrations', on_delete=models.CASCADE)
    integration_type = models.ForeignKey(IntegrationType, related_name='integrations', on_delete=models.CASCADE)
    pass


class Project(models.Model):
    workspace = models.ForeignKey(Workspace, related_name='projects', on_delete=models.CASCADE)
    pass
