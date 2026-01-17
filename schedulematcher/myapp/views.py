from django.shortcuts import render, HttpResponse

# Create your views here.

def welcomepage(request):
    return render(request, "welcomepage.html")

def home(request):
    return render(request, 'home.html')

def createaccount(request):
    return render(request, "createaccount.html")

<<<<<<< HEAD
def creategroup(request):
=======
def creategroupe(request):
>>>>>>> db770b5 (more ui?)
    return render(request, "creategroupe.html")
