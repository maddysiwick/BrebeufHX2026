from django.shortcuts import render, HttpResponse
from .models import Schedule,Block,Day

# Create your views here.

def welcomepage(request):
    return render(request, "welcomepage.html")

def home(request):
    return render(request, 'home.html')

def createaccount(request):
    return render(request, "createaccount.html")

<<<<<<< HEAD
def dummy(request):
    schedule=Schedule.objects.get(pk=1)
    mondayBlocks=schedule.monday.block_set.all()
    return render (request,"dummy.html",{"class":mondayBlocks[0]})
=======
def creategroup(request):
    return render(request, "creategroup.html")
>>>>>>> 60457fb007f1c005648706d6811b614082f08fcc
