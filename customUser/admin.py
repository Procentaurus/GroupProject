from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import *

class MyUserAdmin(UserAdmin):
    model = MyUser
    list_display = ("email", "username", "phone_number")
    list_filter = ("email", "username")
    readonly_fields = ("last_login", "creation_date")
    search_fields = ("email",)
    ordering = ("email",)
    fieldsets = (
        ("Main section", {"fields": ("email", "username","phone_number", "password")}),
        ("Additional", {"fields": ("hide_contact_data", "is_active", "is_admin")}),
        ("Set up", {"fields": ("last_login", "creation_date")}),
    )
    add_fieldsets = (
        ("Main section", {"fields": ("email", "username", "phone_number", "password1", "password2")}),
        ("Additional", {"fields": ("hide_contact_data", "is_active", "is_admin")}),
    )
    
admin.site.register(MyUser, MyUserAdmin)
admin.site.unregister(Group)