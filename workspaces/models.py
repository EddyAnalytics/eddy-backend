from django.db import models


class Workspace(models.Model):
    id = models.AutoField(primary_key=True)
    # user is a one to one relation defined in the user model
    # label can be inferred from user label

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='projects', on_delete=models.CASCADE)
    workspace = models.ForeignKey('workspaces.Workspace', related_name='projects', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
