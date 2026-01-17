from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from myapp.models import Block, Day,Schedule,Team,User,Request
from django.core.files.storage import default_storage
import math
import json
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST
from django.http import JsonResponse
# Create your views here.

def welcomepage(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        pass
    else:
        return render(request, "welcomepage.html", {})


def home(request):
    events = []
    
    if request.method == "POST":
        try:
            username = request.POST["username"]
            password = request.POST["password"]

        for week in range(4):
            for day_index, day_blocks in enumerate(schedule):
                for block in day_blocks:
                    # reload block from DB to get correct 'mandatory'
                    db_block = Block.objects.get(id=block.id)

                    block_date = start_date + timedelta(days=weekday_map[day_index] + week*7)

                    start_str = intToTime(block.startTime)
                    end_str = intToTime(block.endTime)
                    start_dt = datetime.fromisoformat(f"{block_date.date()}T{start_str}")
                    end_dt = datetime.fromisoformat(f"{block_date.date()}T{end_str}")

                    events.append({
                        'id': db_block.id,  # use db version
                        'title': db_block.name,
                        'start': start_dt.isoformat(),
                        'end': end_dt.isoformat(),
                        'color': '#007EA7' if db_block.mandatory else '#DFF8FF',
                        'extendedProps': {
                            'mandatory': db_block.mandatory
                        },
                    })



        for i in range(len(schedule)):
            for j in range (len(schedule[i])):
                block = schedule[i][j]
                print(i)
                print(block.name)
                print(block.startTime)
                print(block.endTime)
                      

    return render(request, 'home.html', {'events': events})

def createaccount(request):
    events = []

    if request.method == "POST":
        events = []
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            
            try:
                pdf = request.FILES['pdfFile']
            except:
                return redirect("welcomepage")
            
            # Parse PDF and save schedule to user
            schedule_obj, block_lists = pdfToSchedule(pdf)
            user.schedule = schedule_obj
            user.save()
            
            events = generateVisualSchedule(block_lists)
            return render(request, 'home.html', {'events': events})
        
        
    else:
        form = UserCreationForm()

    return render(request, "createaccount.html", {"form": form})

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
                                           mandatory=schedule["Monday"][i].mandatory,
                                           day=day))

    for i in range(len(schedule["Tuesday"])):
        day = Day.objects.create(name="Tuesday")
        tuesday.append(Block.objects.create(name=schedule["Tuesday"][i].name, 
                                            startTime=timeToInt(schedule["Tuesday"][i].startTime), 
                                            endTime=timeToInt(schedule["Tuesday"][i].endTime),
                                            mandatory=schedule["Tuesday"][i].mandatory,
                                            day=day))
    
    for i in range(len(schedule["Wednesday"])):
        day = Day.objects.create(name="Wednesday")
        wednesday.append(Block.objects.create(name=schedule["Wednesday"][i].name, 
                                              startTime=timeToInt(schedule["Wednesday"][i].startTime), 
                                              endTime=timeToInt(schedule["Wednesday"][i].endTime),
                                              mandatory=schedule["Wednesday"][i].mandatory,
                                              day=day))
        
    for i in range(len(schedule["Thursday"])):
        day = Day.objects.create(name="Thursday")
        thursday.append(Block.objects.create(name=schedule["Thursday"][i].name, 
                                             startTime=timeToInt(schedule["Thursday"][i].startTime), 
                                             endTime=timeToInt(schedule["Thursday"][i].endTime),
                                             mandatory=schedule["Thursday"][i].mandatory,
                                             day=day))
        
    for i in range(len(schedule["Friday"])):
        day = Day.objects.create(name="Friday")
        friday.append(Block.objects.create(name=schedule["Friday"][i].name, 
                                           startTime=timeToInt(schedule["Friday"][i].startTime), 
                                           endTime=timeToInt(schedule["Friday"][i].endTime),
                                           mandatory=schedule["Friday"][i].mandatory,
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
    group2=Team.objects.create(name="french project")
    group2.members.add(User.objects.get(pk=1))
    request1=Request.objects.create(message="you have been invited to join a new group",receptor=request.user,sender=group2)
    schedules=[]
    for member in group2.members.all():
        schedules.append(member.schedule)
    results=findVacantPlage(schedules,120)
    return render (request,"dummy.html",{"vacantPlages":results})

#im sorry for the unholy number of loops
#it's fine it won't grow nearly to the size needed to become slow
def findVacantPlage(schedules, blockSize, earliest=480, latest=1200):
    blocks=[[],[],[],[],[],[],[]]
    for schedule in schedules:
        days=[schedule.monday,schedule.tuesday,schedule.wednesday,schedule.thursday,schedule.friday,schedule.saturday,schedule.sunday]
        for i in range(len(days)):
            for block in days[i].block_set.all():
                blocks[i].append((block.startTime,block.endTime))
    plage=[[],[],[],[],[],[],[]]
    candidates=[[],[],[],[],[],[],[]]

    for i in range(earliest,latest,15):
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
    if request.method == "POST":
        print(request)
        # User.objects.get()
    

    return render(request, "creategroup.html")

def match(request):
    return render(request, "match.html")



@require_POST
def toggle_mandatory(request, block_id):
    print("toggled")
    data = json.loads(request.body)

    block = Block.objects.get(id=block_id)
    print( data["mandatory"])
    block.mandatory = data["mandatory"]
    block.save()

    return JsonResponse({"success": True})

