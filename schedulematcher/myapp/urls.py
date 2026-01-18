from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import toggle_mandatory

urlpatterns = [
    path("", views.welcomepage, name="welcomepage"),
    path("home/", views.home, name="home"),
    path('groups/<int:id>/', views.groupDetail, name='group_detail'),
    path("createaccount/", views.createaccount, name="createaccount"),
    path("login/", views.createaccount, name="login"),
    path("login/", include("django.contrib.auth.urls")),
    path("creategroup/", views.creategroup, name="creategroup"),
    path("createevent/", views.createCalendarEvent, name="createevent"),
    path("get-requests/", views.getRequests, name="get-requests"),
    path("accept-request/<int:request_id>/", views.accept_request, name="accept-request"),
    path("reject-request/<int:request_id>/", views.reject_request, name="reject-request"),
    path('toggle-mandatory/<int:block_id>/', toggle_mandatory, name='toggle_mandatory'),
    path('logout/', views.logout_view, name='logout'),
    path('findcommontime/<int:team_id>/', views.findCommonTime, name='findcommontime'),
    path('rename-group/<int:team_id>/', views.renameGroup, name='rename-group'),
    path('leave-group/<int:team_id>/', views.leaveGroup, name='leave-group'),
    path('delete-event/<int:block_id>/', views.deleteCalendarEvent, name='delete-event'),
    path('update-event/<int:block_id>/', views.updateCalendarEvent, name='update-event'),
    path('upload-schedule/', views.uploadSchedule, name='uploadschedule'),
    path('clear-schedule/', views.clearSchedule, name='clearschedule'),
    path('add-member/<int:team_id>/', views.addMember, name='add-member'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)