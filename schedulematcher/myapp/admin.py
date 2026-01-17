from django.contrib import admin
from .models import Block,Schedule,Day,Team,User

admin.site.register(Block)
admin.site.register(Schedule)
admin.site.register(Day)
admin.site.register(Team)
admin.site.register(User)