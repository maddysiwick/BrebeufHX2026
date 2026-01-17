from django.shortcuts import render, HttpResponse
from myapp.parser.parser import OmnivoxScheduleParser
from myapp.models import Block, Day,Schedule
from django.core.files.storage import default_storage
import os
# Create your views here.

def welcomepage(request):
    return render(request, "welcomepage.html")

def home(request):
    if request.method == "POST":
        pdf = request.FILES['pdfFile']
        schedule = convert(pdf) # List of 5 lists each containing blocks
        
    return render(request, 'home.html')

def createaccount(request):
    return render(request, "createaccount.html")

def creategroup(request):
    return render(request, "creategroup.html")


def convert(pdf):
    parse = OmnivoxScheduleParser(pdf)
    schedule = parse.parseCourses()

    monday = []
    tuesday = []
    wednesday = []
    thursday = []
    friday = []

    for i in range(len(schedule["Monday"])):
        day = Day.objects.create(name="Monday")
        monday.append(Block.objects.create(name=schedule["Monday"][i].name, 
                                           startTime=timeToInt(schedule["Monday"][i].startTime), 
                                           endTime=timeToInt(schedule["Monday"][i].endTime),
                                           mandatory=True,
                                           day=day))

    for i in range(len(schedule["Tuesday"])):
        day = Day.objects.create(name="Tuesday")
        tuesday.append(Block.objects.create(name=schedule["Tuesday"][i].name, 
                                            startTime=timeToInt(schedule["Tuesday"][i].startTime), 
                                            endTime=timeToInt(schedule["Tuesday"][i].endTime),
                                            mandatory=True,
                                            day=day))
    
    for i in range(len(schedule["Wednesday"])):
        day = Day.objects.create(name="Wednesday")
        wednesday.append(Block.objects.create(name=schedule["Wednesday"][i].name, 
                                              startTime=timeToInt(schedule["Wednesday"][i].startTime), 
                                              endTime=timeToInt(schedule["Wednesday"][i].endTime),
                                              mandatory=True,
                                              day=day))
        
    for i in range(len(schedule["Thursday"])):
        day = Day.objects.create(name="Thursday")
        thursday.append(Block.objects.create(name=schedule["Thursday"][i].name, 
                                             startTime=timeToInt(schedule["Thursday"][i].startTime), 
                                             endTime=timeToInt(schedule["Thursday"][i].endTime),
                                             mandatory=True,
                                             day=day))
        
    for i in range(len(schedule["Friday"])):
        day = Day.objects.create(name="Friday")
        friday.append(Block.objects.create(name=schedule["Friday"][i].name, 
                                           startTime=timeToInt(schedule["Friday"][i].startTime), 
                                           endTime=timeToInt(schedule["Friday"][i].endTime),
                                           mandatory=True,
                                           day=day))
    
    return [monday, tuesday, wednesday, thursday, friday]

def timeToInt(time):
    hour = int(time.split(":")[0])
    minute = int(time.split(":")[1])
    
    return hour*60 + minute
    
def dummy(request):
    schedule=Schedule.objects.get(pk=1)
    mondayBlocks=schedule.monday.block_set.all()
    return render (request,"dummy.html",{"class":mondayBlocks[0]})
def creategroup(request):
    return render(request, "creategroup.html")

def match(request):
    return render(request, "match.html")