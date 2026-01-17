from django.urls import path
from . import views


urlpatterns = [
    path("", views.welcomepage, name="welcomepage"),
    path("home/", views.home, name="home"),
    path("createaccount/", views.createaccount, name="createaccount"),
<<<<<<< HEAD
    path("login/", views.createaccount, name="login"),
    path("creategroup/", views.creategroup, name="creategroup"),
=======
    path("creategroupe/", views.creategroupe, name="creategroupe"),
>>>>>>> db770b5 (more ui?)
]