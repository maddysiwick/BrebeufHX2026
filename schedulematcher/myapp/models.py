from django.db import models
from django.contrib.auth import AbstractUser

class User(AbstractUser):
    pass

class Block(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    mandatory = models.BooleanField()












