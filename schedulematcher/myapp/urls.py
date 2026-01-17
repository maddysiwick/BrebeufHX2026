from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.welcomepage, name="welcomepage"),
    path("home/", views.home, name="home"),
    path("dummy/",views.dummy,name="dummy"),
    path("createaccount/", views.createaccount, name="createaccount"),
    path("login/", views.createaccount, name="login"),
    path("login/", include("django.contrib.auth.urls")),
    path("creategroup/", views.creategroup, name="creategroup"),
    path("match/", views.match, name="match"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)