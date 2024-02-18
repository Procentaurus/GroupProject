from django.contrib import admin
from .models import *


#
# Each class adds one entity class and its elements to django admin, with specified values for display and search
#

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher_player', 'student_player')
    readonly_fields = ('id',)
    add_fieldsets = (
        ("Main section", {"fields": (
            "teacher_player",'student_player',
            "next_move_player", "next_move_type")
        }),
    )

@admin.register(GameUser)
class GameUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'conflict_side')
    readonly_fields = ('id',)
    add_fieldsets = (
        ("Main section", {"fields": ("user",'conflict_side')}),
    )

@admin.register(GameAuthenticationToken)
class GameAuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'issued')
    readonly_fields = ('id','issued')
    ordering = ("-issued",)
    add_fieldsets = (
        ("Main section", {"fields": ("user",)}),
    )