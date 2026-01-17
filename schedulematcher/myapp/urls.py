from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import toggle_mandatory

urlpatterns = [
    path("", views.welcomepage, name="welcomepage"),
    path("home/", views.home, name="home"),
    path("dummy/",views.dummy,name="dummy"),
    path("createaccount/", views.createaccount, name="createaccount"),
    path("login/", views.createaccount, name="login"),
    path("login/", include("django.contrib.auth.urls")),
    path("creategroup/", views.creategroup, name="creategroup"),
    path("createevent/", views.createCalendarEvent, name="createevent"),
    path("get-requests/", views.getRequests, name="get-requests"),
    path("match/", views.match, name="match"),
    path('toggle-mandatory/<int:block_id>/', toggle_mandatory, name='toggle_mandatory'),
    path('logout/', views.logout_view, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)