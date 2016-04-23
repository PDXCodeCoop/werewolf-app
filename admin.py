from django.contrib import admin
from models import *

class PlayerInline(admin.TabularInline):
    model = Player

class TurnInline(admin.TabularInline):
    model = Turn

class VoteInline(admin.TabularInline):
    model = Vote
    include = ['players', ]

@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    inlines = [ VoteInline]

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [ PlayerInline, TurnInline]


# Register your models here.
admin.site.register(Room)
admin.site.register(Player)
admin.site.register(Role)
admin.site.register(Vote)
