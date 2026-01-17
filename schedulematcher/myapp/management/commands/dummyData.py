from django.core.management.base import BaseCommand
from myapp.models import Block,Schedule,Day

class Command(BaseCommand):
    def handle(self, *args, **options):
        day1=Day.objects.create(name="monday")
        day2=Day.objects.create(name="tuesday")
        day3=Day.objects.create(name="wednesday")
        day4=Day.objects.create(name="thursday")
        day5=Day.objects.create(name="friday")
        day6=Day.objects.create(name="saturday")
        day7=Day.objects.create(name="sunday")

        Block.objects.create(name="Vertebretes",day=day2,startTime=540,endTime=720,mandatory=True)
        Block.objects.create(name="English",day=day3,startTime=480,endTime=600,mandatory=False)
        Block.objects.create(name="Chemistry of the environment",day=day4,startTime=600,endTime=780,mandatory=True)

        Schedule.objects.create(monday=day1,tuesday=day2,wednesday=day3,thursday=day4,friday=day5,saturday=day6,sunday=day7)
        print("dummy data hehe")