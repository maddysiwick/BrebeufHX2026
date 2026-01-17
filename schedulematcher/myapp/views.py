from django.shortcuts import render, HttpResponse

# Create your views here.

def welcomepage(request):
    return render(request, "welcomepage.html")

def home(request):
    return render(request, "home.html")

def home(request):
    return render(request, "createaccount.html")
