from django.urls import path
from . import views


urlpatterns = [
    path("", views.welcomepage, name="welcomepage"),
    path("home/", views.home, name="home"),
    path("dummy/",views.dummy,name="dummy"),
    path("createaccount/", views.createaccount, name="createaccount"),
    path("login/", views.createaccount, name="login"),
    path("creategroup/", views.creategroup, name="creategroup"),
    path("match/", views.match, name="match"),
]