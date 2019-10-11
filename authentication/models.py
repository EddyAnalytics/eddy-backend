from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from workspaces.models import Workspace


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    # user reference is not necessary here
    # label is username
    workspace = models.OneToOneField('workspaces.Workspace', models.CASCADE, related_name='user')

    def __str__(self):
        return self.username


@receiver(pre_save, sender=User)
def pre_save_user(signal, sender, instance: User, using, **kwargs):
    user = instance
    if not hasattr(user, 'workspace'):
        workspace = Workspace()
        workspace.save()
        user.workspace_id = workspace.id


@receiver(post_delete, sender=User)
def post_delete_user(signal, sender, instance: User, using, **kwargs):
    user = instance
    workspace = user.workspace
    workspace.delete()
