from django.urls import path
from . import views


urlpatterns = [
    path("", views.welcomepage, name="welcomepage"),
    path("home/", views.home, name="home"),
    path("createaccount/", views.createaccount, name="createaccount"),
<<<<<<< HEAD
    path("login/", views.createaccount, name="login"),
=======
>>>>>>> 1dfd7d2 (url fixes)
]