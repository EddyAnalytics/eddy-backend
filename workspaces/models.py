from django.db import models


class Workspace(models.Model):
    id = models.AutoField(primary_key=True)

    # user is a one to one relation defined in the user model
    # label can be inferred from user label

    def __str__(self):
        return 'Workspace' + ' ' + self.user.username
