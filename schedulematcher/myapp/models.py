from django.db import models
from django.contrib.auth.models import AbstractUser


class Day(models.Model):
    name=models.CharField(max_length=100)

class Block(models.Model):
    name = models.CharField(max_length=100)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    startTime = models.IntegerField()
    endTime = models.IntegerField()
    mandatory = models.BooleanField()

class Schedule(models.Model):
    monday=models.ForeignKey(Day,on_delete=models.CASCADE,related_name="monday")
    tuesday=models.ForeignKey(Day,on_delete=models.CASCADE,related_name="tuesday")
    wednesday=models.ForeignKey(Day,on_delete=models.CASCADE,related_name="wednesday")
    thursday=models.ForeignKey(Day,on_delete=models.CASCADE,related_name="thursday")
    friday=models.ForeignKey(Day,on_delete=models.CASCADE,related_name="friday")
    saturday=models.ForeignKey(Day,on_delete=models.CASCADE,related_name="saturday")
    sunday=models.ForeignKey(Day,on_delete=models.CASCADE,related_name="sunday")

class User(AbstractUser):
    schedule=models.ForeignKey(Schedule,on_delete=models.CASCADE,null=True)
    pdfFile = models.FileField(upload_to='pdfs/', null=True, blank=True)

class Team(models.Model):
    members=models.ManyToManyField(User)
    name=models.CharField(max_length=100)
    plannedMeetings=models.JSONField(default=list,null=True)
    meetingSuggestions=models.JSONField(default=dict,null=True)

class Request(models.Model):
    message=models.CharField(max_length=200)
    receptor=models.ForeignKey(User,on_delete=models.SET_NULL)
    sender=models.ForeignKey(Team,on_delete=models.SET_NULL)
    
