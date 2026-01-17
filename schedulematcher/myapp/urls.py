from django.urls import path
from . import views


urlpatterns = [
    path("", views.welcomepage, name="welcomepage"),
    path("home/", views.home, name="home"),
<<<<<<< HEAD
    path("createaccount/", views.home, name="createaccount"),
    path("dummy/",views.dummy,name="dummy")
=======
    path("createaccount/", views.createaccount, name="createaccount"),
    path("login/", views.createaccount, name="login"),
    path("creategroup/", views.creategroup, name="creategroup"),
>>>>>>> 60457fb007f1c005648706d6811b614082f08fcc
]