from django.contrib import admin
from .models import *


#
# Each class adds one entity class and its elements to django admin, with specified values for display and search
#

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher_player', 'student_player', 'start_datetime', 'end_datetime')
    readonly_fields = ('id', 'start_datetime', 'end_datetime')
    ordering = ("-start_datetime",)
    add_fieldsets = (
        ("Main section", {"fields": ("teacher_player",'student_player', "next_move")}),
    )

@admin.register(GameUser)
class GameUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'conflict_side', 'in_game')
    readonly_fields = ('id',)
    add_fieldsets = (
        ("Main section", {"fields": ("user",'conflict_side', 'in_game')}),
    )

@admin.register(GameAuthenticationToken)
class GameAuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'issued')
    readonly_fields = ('id','issued')
    ordering = ("-issued",)
    add_fieldsets = (
        ("Main section", {"fields": ("user",)}),
    )