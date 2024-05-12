from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models.my_user.my_user import MyUser
from .models.game_archive.game_archive import GameArchive


class MyUserAdmin(UserAdmin): # used in django admin, enables more data for admin's view
    model = MyUser
    list_display = ("id", "email", "username", "phone_number")
    list_filter = ("email", "username")
    readonly_fields = ("id", "last_login", "creation_date")
    search_fields = ("email",)
    ordering = ("email",)
    fieldsets = (
        ("Main section",
            {"fields": ("email", "username", "phone_number", "password")}
        ),
        ("Additional",
            {"fields": ("in_game", "hide_contact_data", "is_active", "is_admin",
                        'games_won', 'games_played')}
        ),
        ("Set up", {"fields": ("id", "last_login", "creation_date", "bio")}),
    )
    add_fieldsets = (
        ("Main section",
            {"fields": (
                "email", "username", "phone_number", "password1", "password2")
            }
        ),
        ("Additional",
            {"fields": ("hide_contact_data", "is_active", "is_admin")}
        ),
    )


@admin.register(GameArchive)
class GameArchiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date', 'teacher_player', 'student_player')
    readonly_fields = ('id',)
    ordering = ('-start_date', "-start_time")
    add_fieldsets = ((
        "Players", {"fields": (
            "teacher_player",'student_player'
            )},
        "Game info", {"fields":('start_date', 'start_time',
            'lenght_in_sec', 'winner')}
        ),
    )


admin.site.register(MyUser, MyUserAdmin)
admin.site.unregister(Group)
