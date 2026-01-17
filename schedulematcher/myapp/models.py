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

class Schedule(models.Model):
    monday=models.ForeignKey(Day)
    tuesday=models.ForeignKey(Day)
    wednesday=models.ForeignKey(Day)
    thursday=models.ForeignKey(Day)
    friday=models.ForeignKey(Day)
    saturday=models.ForeignKey(Day)
    sunday=models.ForeignKey(Day)

















