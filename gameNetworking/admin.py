from django.contrib import admin
from .models import *

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher_player', 'student_player', 'start_datetime', 'end_datetime')
    readonly_fields = ('id', 'teacher_player', 'student_player', 'start_datetime', 'end_datetime')
    ordering = ("-start_datetime",)

@admin.register(GameUser)
class GameWaitingUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'conflict_side', 'in_game')
    readonly_fields = ("id", "user_id", "in_game")

@admin.register(GameAuthenticationToken)
class GameAuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'issued')
    readonly_fields = ('id', 'user_id', 'issued')
    ordering = ("-issued",)