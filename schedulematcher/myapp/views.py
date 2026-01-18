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

def asJSON(request):
    return json.loads(request.body.decode(encoding="utf-8", errors="strict"))

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
            return redirect('welcomepage')

    if not request.user.is_authenticated:
        return redirect("welcomepage")
    
    if request.user.is_authenticated and request.user.schedule:
        schedule = request.user.schedule
        days = [schedule.monday, schedule.tuesday, schedule.wednesday, schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday]
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

def renameGroup(request, team_id):
    if request.method != "POST":
        return JsonResponse({"success": False})
    
    team = Team.objects.get(id=team_id)
    if request.user is None or request.user not in team.members.all():
        return JsonResponse({"success": False})
    
    team.name = asJSON(request)["name"]
    team.save()
    return JsonResponse({"success": True})

def leaveGroup(request, team_id):
    team = Team.objects.get(id=team_id)
    if request.user is None or request.user not in team.members.all():
        return JsonResponse({"success": False})
    
    team.members.remove(request.user)
    return JsonResponse({"success": True})

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
        days = [schedule.monday, schedule.tuesday, schedule.wednesday, schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday]
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
            days = [schedule.monday, schedule.tuesday, schedule.wednesday, schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday]
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
            try:
                receptor = User.objects.get(username=member)
                TeamRequest.objects.create(message=f"{request.user.username} invited you to join {team.name}", sender=team, receptor=receptor)
            except User.DoesNotExist:
                continue
        
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
    
    isRecurring = data.get("isRecurring", True)
    specificDate = data.get("specificDate", None)
    repeatCount = data.get("repeatCount", 0)  # 0 means infinite/weekly
    
    created_blocks = []
    
    if isRecurring:
        # Weekly recurring event - just create one block
        block = Block.objects.create(
            name=data["name"], 
            day=day, 
            startTime=data["startTime"], 
            endTime=data["endTime"], 
            mandatory=data.get("mandatory", False),
            isRecurring=True,
            specificDate=None
        )
        created_blocks.append(block.id)
    else:
        # One-time or repeat for N weeks
        from datetime import datetime, timedelta
        base_date = datetime.fromisoformat(specificDate).date() if specificDate else None
        
        if repeatCount > 0:
            # Create N one-time events
            for i in range(repeatCount):
                event_date = base_date + timedelta(weeks=i) if base_date else None
                block = Block.objects.create(
                    name=data["name"], 
                    day=day, 
                    startTime=data["startTime"], 
                    endTime=data["endTime"], 
                    mandatory=data.get("mandatory", False),
                    isRecurring=False,
                    specificDate=event_date
                )
                created_blocks.append(block.id)
        else:
            # Single one-time event
            block = Block.objects.create(
                name=data["name"], 
                day=day, 
                startTime=data["startTime"], 
                endTime=data["endTime"], 
                mandatory=data.get("mandatory", False),
                isRecurring=False,
                specificDate=base_date
            )
            created_blocks.append(block.id)
    
    return JsonResponse({"success": True, "block_ids": created_blocks})


def deleteCalendarEvent(request, block_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"})
    
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Not authenticated"})
    
    schedule = request.user.schedule
    if not schedule:
        return JsonResponse({"success": False, "error": "No schedule found"})
    
    # Get all days from user's schedule
    user_days = [schedule.monday, schedule.tuesday, schedule.wednesday, 
                 schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday]
    user_day_ids = [d.id for d in user_days]
    
    try:
        block = Block.objects.get(id=block_id)
        # Check if this block belongs to the user's schedule
        if block.day.id not in user_day_ids:
            return JsonResponse({"success": False, "error": "Not your event"})
        
        block.delete()
        return JsonResponse({"success": True})
    except Block.DoesNotExist:
        return JsonResponse({"success": False, "error": "Event not found"})


def updateCalendarEvent(request, block_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"})
    
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Not authenticated"})
    
    schedule = request.user.schedule
    if not schedule:
        return JsonResponse({"success": False, "error": "No schedule found"})
    
    # Get all days from user's schedule
    user_days = [schedule.monday, schedule.tuesday, schedule.wednesday, 
                 schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday]
    user_day_ids = [d.id for d in user_days]
    
    try:
        block = Block.objects.get(id=block_id)
        # Check if this block belongs to the user's schedule
        if block.day.id not in user_day_ids:
            return JsonResponse({"success": False, "error": "Not your event"})
        
        data = json.loads(request.body.decode(encoding="utf-8", errors="strict"))
        
        # Update day if provided
        if "day" in data:
            new_day_index = data["day"]
            block.day = user_days[new_day_index]
        
        # Update times if provided
        if "startTime" in data:
            block.startTime = data["startTime"]
        if "endTime" in data:
            block.endTime = data["endTime"]
        
        block.save()
        return JsonResponse({"success": True})
    except Block.DoesNotExist:
        return JsonResponse({"success": False, "error": "Event not found"})


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
    
    vacant_slots, scored_events = findVacantPlage(schedules, duration, start_date=datetime(2026, 1, 5))
    
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    events = []
    max_score = -1
    best_slot_idx = -1

    for i, slot in enumerate(scored_events):
        if slot['score'] > max_score:
            max_score = slot['score']
            best_slot_idx = i

    for i, slot in enumerate(scored_events):
        start_dt = datetime.fromisoformat(slot['start'])
        end_dt = datetime.fromisoformat(slot['end'])
        day_index = (start_dt.weekday()) % 7 # 0 is Monday
        
        events.append({
            'title': 'Available',
            'start': slot['start'],
            'end': slot['end'],
            'color': '#28a745',
            'day': day_index,
            'dayName': day_names[day_index],
            'startTime': (start_dt.hour * 60 + start_dt.minute),
            'endTime': (end_dt.hour * 60 + end_dt.minute),
            'score': slot['score'],
            'isRecommended': (i == best_slot_idx and slot['score'] > 0)
        })
    
    return JsonResponse({"success": True, "events": events})


def logout_view(request):
    logout(request)
    return redirect("welcomepage")


def dummy(request):
    group2=Team.objects.create(name="french project")
    group2.members.add(User.objects.get(pk=1))
    request1=TeamRequest.objects.create(message=f"{request.user.username} invited you to join {group2.name}",receptor=request.user,sender=group2)
    schedules=[]
    for member in group2.members.all():
        schedules.append(member.schedule)
    results=findVacantPlage(schedules,120)
    return render (request,"dummy.html",{"vacantPlages":results})


def checkTeamRequests(request):
    requests= request.user.request_set.all()
    print(requests)

def accept_request(request, request_id):
    if request.method != "POST":
        return redirect("home")
    
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Not authenticated"})
    
    try:
        team_request = TeamRequest.objects.get(id=request_id, receptor=request.user)
        team = team_request.sender
        team.members.add(request.user)
        team_request.delete()
        return JsonResponse({"success": True})
    except TeamRequest.DoesNotExist:
        return JsonResponse({"success": False, "error": "Request not found"})

def reject_request(request, request_id):
    if request.method != "POST":
        return redirect("home")
    
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Not authenticated"})
    
    try:
        team_request = TeamRequest.objects.get(id=request_id, receptor=request.user)
        team_request.delete()
        return JsonResponse({"success": True})
    except TeamRequest.DoesNotExist:
        return JsonResponse({"success": False, "error": "Request not found"})

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


def uploadSchedule(request):
    if request.method != "POST":
        return redirect("home")
    
    if not request.user.is_authenticated:
        return redirect("welcomepage")
    
    if 'schedule_pdf' not in request.FILES:
        messages.error(request, "No file uploaded")
        return redirect("home")
    
    pdf_file = request.FILES['schedule_pdf']
    
    if request.user.pdfFile:
        request.user.pdfFile.delete()
    
    try:
        if request.user.schedule:
            schedule = request.user.schedule
            days = [schedule.monday, schedule.tuesday, schedule.wednesday, 
                    schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday]
            for day in days:
                day.block_set.all().delete()
        
        schedule_obj, block_lists = pdfToSchedule(pdf_file)
        request.user.schedule = schedule_obj
        request.user.save()
        
        messages.success(request, "Schedule uploaded successfully!")
    except Exception as e:
        print(f"Error parsing schedule: {str(e)}")
        messages.error(request, f"Error parsing schedule: {str(e)}")
    
    return redirect("home")


def clearSchedule(request):
    if request.method != "POST":
        return redirect("home")
    
    if not request.user.is_authenticated:
        return redirect("welcomepage")
    
    if request.user.pdfFile:
        request.user.pdfFile.delete()
        request.user.pdfFile = None
        request.user.save()
    
    if request.user.schedule:
        schedule = request.user.schedule
        days = [schedule.monday, schedule.tuesday, schedule.wednesday, 
                schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday]
        for day in days:
            day.block_set.all().delete()
    
    messages.success(request, "Schedule cleared!")
    return redirect("home")


def addMember(request, team_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"})
    
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Not authenticated"})
    
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"success": False, "error": "Team not found"})
    
    if request.user not in team.members.all():
        return JsonResponse({"success": False, "error": "You are not a member of this team"})
    
    data = asJSON(request)
    username = data.get("username", "")
    
    if not username:
        return JsonResponse({"success": False, "error": "No username provided"})
    
    try:
        receptor = User.objects.get(username=username)
        
        if receptor in team.members.all():
            return JsonResponse({"success": False, "error": "User is already a member"})
        
        existing = TeamRequest.objects.filter(sender=team, receptor=receptor).first()
        if existing:
            return JsonResponse({"success": False, "error": "Invite already sent"})
        
        TeamRequest.objects.create(
            message=f"{request.user.username} invited you to join {team.name}",
            sender=team,
            receptor=receptor
        )
        return JsonResponse({"success": True})
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "User not found"})