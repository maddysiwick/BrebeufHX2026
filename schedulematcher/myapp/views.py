from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from myapp.models import Block, Day,Schedule,Team,User,Request as TeamRequest
from myapp.forms import CustomUserCreationForm
import random, string, hashlib, colorsys
import json 
from myapp.schedule.scheduler import pdfToSchedule, generateVisualSchedule, findVacantPlage
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import datetime, timedelta
from myapp.models import Block, Day,Schedule,Team,User

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
    # checkTeamRequests(request)
    
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

    if not request.user.is_authenticated:
        return redirect("welcomepage")
    
    if request.user.is_authenticated and request.user.schedule:
        schedule = request.user.schedule
        days = [schedule.monday, schedule.tuesday, schedule.wednesday, schedule.thursday, schedule.friday]
        block_lists = [list(day.block_set.all()) for day in days]
        events = generateVisualSchedule(block_lists)

    user_teams = Team.objects.filter(members=request.user)

    return render(request, 'home.html', {'events': events, 'user': request.user, 'teams': user_teams})

def generateRandomColor(seed_text=None):
    if seed_text:
        seed = int(hashlib.sha256(seed_text.encode('utf-8')).hexdigest(), 16)
        random_gen = random.Random(seed)
    else:
        random_gen = random.Random()

    h = random_gen.random()
    s = 0.65 + random_gen.random() * 0.2
    l = 0.35 + random_gen.random() * 0.2
    
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    color = '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))

    if color.upper() == "#007EA7":
        return generateRandomColor((seed_text or "") + "alt")
    
    return color

# terrible implementation cuz its just regular counter but no time to make it a uuid
def groupDetail(request, id):
    team = Team.objects.get(id=id)

    if not request.user.is_authenticated:
        return redirect("welcomepage")

    if request.user not in team.members.all():
        return redirect("home")

    events = []
    if request.user.schedule:
        schedule = request.user.schedule
        days = [schedule.monday, schedule.tuesday, schedule.wednesday, schedule.thursday, schedule.friday]
        block_lists = [list(day.block_set.all()) for day in days]
        events = generateVisualSchedule(block_lists)

    user_teams = Team.objects.filter(members=request.user)

    ColorMapping = {}
    all_events = []
    
    if events:
        all_events.extend(events)

    for user in team.members.all():
        if user == request.user:
            continue

        user_color = generateRandomColor(user.username)
        ColorMapping[user.username] = user_color
        if user.schedule:
            schedule = user.schedule
            days = [schedule.monday, schedule.tuesday, schedule.wednesday, schedule.thursday, schedule.friday]
            block_lists = [list(day.block_set.all()) for day in days]
            member_events = generateVisualSchedule(block_lists, color=user_color)
            all_events.extend(member_events)

    return render(request, 'groups.html', {'currentTeam': team, 'teams': user_teams, 'events': all_events, 'ColorMapping': ColorMapping})

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
        data = json.loads(request.body.decode(encoding="utf-8", errors="strict"))
        team = Team.objects.create(name=data["groupName"])
        team.members.add(request.user)
        
        for member in data["emails"]:
            receptor = User.objects.get(username=member)
            teamInviteRequest = TeamRequest(message="", sender=team, receptor=receptor)
            resolveRequest(teamInviteRequest)
        
        return JsonResponse({"success": True, "team_id": team.id})
    
    # Get user's teams for sidebar
    user_teams = Team.objects.filter(members=request.user)
    return render(request, "creategroup.html", {"teams": user_teams, "isGroupCreationPage": True})

def getRequests(request):
    requests = TeamRequest.objects.filter(receptor=request.user)
    return JsonResponse({"requests": list(requests.values())})

def createCalendarEvent(request):
    if request.method != "POST":
        return redirect("home")
    
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Not authenticated"})
    
    data = json.loads(request.body.decode(encoding="utf-8", errors="strict"))
    
    schedule = request.user.schedule
    if not schedule:
        return JsonResponse({"success": False, "error": "No schedule found for user"})
    
    days = [schedule.monday, schedule.tuesday, schedule.wednesday, schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday]
    day = days[data["day"]]
    
    Block.objects.create(name=data["name"], day=day, startTime=data["startTime"], endTime=data["endTime"], mandatory=data.get("mandatory", True))
    return JsonResponse({"success": True})


def findCommonTime(request, team_id):
    if request.method != "POST":
        return redirect("home")
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"})
    
    team = Team.objects.get(id=team_id)
    
    if request.user not in team.members.all():
        return JsonResponse({"error": "Not a member of this team"})
    
    data = json.loads(request.body.decode(encoding="utf-8", errors="strict"))
    duration = data.get("duration", 60)
    
    schedules = []
    for member in team.members.all():
        if member.schedule:
            schedules.append(member.schedule)
    
    if not schedules:
        return JsonResponse({"error": "No schedules found for team members"})
    
    vacant_slots = findVacantPlage(schedules, duration)
    
    start_date = datetime(2026, 1, 5)
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    events = []
    for day_index, day_slots in enumerate(vacant_slots):
        day_date = start_date + timedelta(days=day_index)
        for slot in day_slots:
            start_minutes, end_minutes = slot
            start_dt = day_date.replace(hour=start_minutes // 60, minute=start_minutes % 60)
            end_dt = day_date.replace(hour=end_minutes // 60, minute=end_minutes % 60)
            events.append({
                'title': 'Available',
                'start': start_dt.isoformat(),
                'end': end_dt.isoformat(),
                'color': '#28a745',
                'day': day_index,
                'dayName': day_names[day_index],
                'startTime': start_minutes,
                'endTime': end_minutes
            })
    
    return JsonResponse({"success": True, "events": events})


def logout_view(request):
    logout(request)
    return redirect("welcomepage")


def dummy(request):
    group2=Team.objects.create(name="french project")
    group2.members.add(User.objects.get(pk=1))
    request1=TeamRequest.objects.create(message="you have been invited to join a new group",receptor=request.user,sender=group2)
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
    plage=findScheduleOverlap(blockSize,blocks)
    if plage==[[],[],[],[],[],[],[]]:
        blocks=[[],[],[],[],[],[],[]]
        for schedule in schedules:
            days=[schedule.monday,schedule.tuesday,schedule.wednesday,schedule.thursday,schedule.friday,schedule.saturday,schedule.sunday]
            for i in range(len(days)):
                for block in days[i].block_set.all():
                    if block.mandatory:
                        blocks[i].append((block.startTime,block.endTime))
        plage=findScheduleOverlap(blockSize,blocks)
    return plage
            
def findScheduleOverlap(blockSize,blocks, earliest=480, latest=1200):
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

def checkTeamRequests(request):
    requests= request.user.request_set.all()
    print(requests)

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
    block_size = 30
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

def logout_view(request):
    logout(request)
    return render(request,"welcomepage.html")