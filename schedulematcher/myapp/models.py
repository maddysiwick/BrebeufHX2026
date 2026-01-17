from django.db import models

class Schedule(models.Model):
    monday=models.ForeignKey(Day)
    tuesday=models.ForeignKey(Day)
    wednesday=models.ForeignKey(Day)
    thursday=models.ForeignKey(Day)
    friday=models.ForeignKey(Day)
    saturday=models.ForeignKey(Day)
    sunday=models.ForeignKey(Day)

