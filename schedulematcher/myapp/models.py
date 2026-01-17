from django.db import models
from django.contrib.auth.models import AbstractUser


class Day(models.Model):
    name=models.CharField(max_length=100)

class Block(models.Model):
    name = models.CharField(max_length=100)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    mandatory = models.BooleanField()

class Schedule(models.Model):
    monday=models.ForeignKey(Day, on_delete=models.CASCADE)
    tuesday=models.ForeignKey(Day, on_delete=models.CASCADE)
    wednesday=models.ForeignKey(Day, on_delete=models.CASCADE)
    thursday=models.ForeignKey(Day, on_delete=models.CASCADE)
    friday=models.ForeignKey(Day, on_delete=models.CASCADE)
    saturday=models.ForeignKey(Day, on_delete=models.CASCADE)
    sunday=models.ForeignKey(Day, on_delete=models.CASCADE)















