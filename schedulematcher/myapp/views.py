from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from myapp.models import Block, Day,Schedule,Team,User,Request
from django.core.files.storage import default_storage
import math
from .forms import CustomUserCreationForm

from myapp.schedule.scheduler import generateVisualSchedule, pdfToSchedule

User = get_user_model()

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
            
            schedule = pdfToSchedule(pdf) # List of 5 lists each containing blocks
            events = generateVisualSchedule(schedule)
            return render(request, 'home.html', {'events': events})
        
        
    else:
        form = UserCreationForm()

    return render(request, "createaccount.html", {"form": form})

def creategroup(request):
    return render(request, "creategroup.html")


def logout_view(request):
    logout(request)


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

def resolveRequest(teamRequest):
    team=teamRequest.sender
    user=teamRequest.receptor
    team.members.add(user)
    Request.objects.delete(teamRequest)