from django.shortcuts import render, HttpResponse
from myapp.parser.parser import OmnivoxScheduleParser
from myapp.models import Block, Day,Schedule,Team,User
from django.core.files.storage import default_storage
import os
import math
# Create your views here.

def welcomepage(request):
    return render(request, "welcomepage.html")

def home(request):
    if request.method == "POST":
        pdf = request.FILES['pdfFile']
        schedule = convert(pdf) # List of 5 lists each containing blocks
        default_storage.save(pdf.name, pdf)
        for i in range(len(schedule)):
            for j in range (len(schedule[i])):
                block = schedule[i][j]
                print(block.name)
                print(block.startTime)
                print(block.endTime)
                      

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

def intToTime(time):
    hour = math.floor(time/60)
    minutes = time % 60
    return str(hour).zfill(2) + ":" + str(minutes).zfill(2)

def dummy(request):
    group1=Team.objects.get(pk=1)
    schedules=[]
    for member in group1.members.all():
        schedules.append(member.schedule)
    results=findVacantPlage(schedules,120)
    return render (request,"dummy.html",{"vacantPlages":results})

#im sorry for the unholy number of loops
def findVacantPlage(schedules, blockSize):
    blocks=[[],[],[],[],[],[],[]]
    for schedule in schedules:
        days=[schedule.monday,schedule.tuesday,schedule.wednesday,schedule.thursday,schedule.friday,schedule.saturday,schedule.sunday]
        for i in range(len(days)):
            for block in days[i].block_set.all():
                blocks[i].append((block.startTime,block.endTime))
    print(blocks)
    plage=[[],[],[],[],[],[],[]]
    candidates=[[],[],[],[],[],[],[]]
    for i in range(480,1200,15):
        for k in range(7):
            toRemove=[]
            for pair in candidates[k]:
                if pair[0]==pair[1]:
                    toRemove.append(pair)
            for pair in toRemove:
                plage[k].append((pair[0]-blockSize,pair[1]))
                candidates[k].remove(pair)
            for l in range(len(candidates[k])):
                candidates[k][l][0]+=15
            toRemove=[]
            for candidate in candidates[k]:
                for block in blocks[k]:
                    if block[0]<candidate[0]<block[1]:
                        toRemove.append(candidate)
                        break
            for item in toRemove:
                candidates[k].remove(item)
            clear=True
            for block in blocks[k]:
                if block[0]<i<block[1]:
                    clear=False
                    break
            if clear:
                candidates[k].append([i,i+blockSize])
    return plage
            


def creategroup(request):
    return render(request, "creategroup.html")

def match(request):
    return render(request, "match.html")
