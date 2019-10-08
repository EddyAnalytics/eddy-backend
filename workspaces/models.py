from django.db import models


class Workspace(models.Model):
    id = models.AutoField(primary_key=True)
    # user is a one to one field in this case defined in the user model


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='projects', on_delete=models.CASCADE)
    workspace = models.ForeignKey('workspaces.Workspace', related_name='projects', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
