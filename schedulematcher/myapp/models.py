from django.db import models
from django.contrib.auth import AbstractUser

class User(AbstractUser):
    pass

class Day(models.Model):
    pass

class Block(models.Model):
    name = models.CharField(max_length=100)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    mandatory = models.BooleanField()















