from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import *

class MyUserAdmin(UserAdmin):
    model = MyUser
    list_display = ("email", "username", "phone_number")
    list_filter = ("email", "username")
    readonly_fields = ("lastLogin", "creationDate")
    search_fields = ("email",)
    ordering = ("email",)
    
admin.site.register(MyUser, MyUserAdmin)
admin.site.unregister(Group)