from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from myapp.models import Block, Day,Schedule,Team,User,Request as TeamRequest
from myapp.forms import CustomUserCreationForm
import random, string
from django.core.files.storage import default_storage
import math
import json 
from myapp.schedule.scheduler import pdfToSchedule, generateVisualSchedule, findVacantPlage
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import datetime, timedelta
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

        except:
            return render(request, 'home.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print("signing in user: "+user.username)
            login(request, user)
            return redirect('home')
        else:
            print("denied")
            messages.success(request, ("Denied"))
            return redirect('welcomepage')
    
    
    if request.user.is_authenticated and request.user.schedule:
        schedule = request.user.schedule
        days = [schedule.monday, schedule.tuesday, schedule.wednesday, schedule.thursday, schedule.friday]
        block_lists = [list(day.block_set.all()) for day in days]
        events = generateVisualSchedule(block_lists)

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
            
            return redirect("home")
        
        
    else:
        form = UserCreationForm()

    return render(request, "createaccount.html", {"form": form})

def creategroup(request):
    if request.method == "POST":
        randomName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        team = Team.objects.create(name=randomName)
        team.members.add(request.user)
        members = json.loads(request.body.decode(encoding="utf-8", errors="strict"))
        
        for member in members:
            receptor = User.objects.get(username=member)
            teamInviteRequest = TeamRequest(message="", sender=team, receptor=receptor)
            resolveRequest(teamInviteRequest)

    return render(request, "creategroup.html")

def match(request):
    return render(request, "match.html")

def resolveRequest(teamRequest):
    team=teamRequest.sender
    user=teamRequest.receptor
    team.members.add(user)
    

    print(team.members.all())
    # TeamRequest.objects.delete(teamRequest)

def dummy(request):
    group2=Team.objects.create(name="french project")
    group2.members.add(User.objects.get(pk=1))
    request1=TeamRequest.objects.create(message="you have been invited to join a new group",receptor=request.user,sender=group2)
    schedules=[]
    for member in group2.members.all():
        schedules.append(member.schedule)
    results=findVacantPlage(schedules,120)
    return render (request,"dummy.html",{"vacantPlages":results})




def match(request):
    schedules = ...
    block_size =30
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())

    plage, events = findVacantPlage(schedules, block_size, start_date=monday)

    return render(request, "match.html", {"events": events})




@require_POST
def toggle_mandatory(request, block_id):
    print("toggled")
    data = json.loads(request.body)

    block = Block.objects.get(id=block_id)
    print( data["mandatory"])
    block.mandatory = data["mandatory"]
    block.save()

    return JsonResponse({"success": True})

