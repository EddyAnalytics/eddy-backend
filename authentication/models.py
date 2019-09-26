from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    requires_superuser = True
    id = models.AutoField(primary_key=True)
