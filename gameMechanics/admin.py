from django.contrib import admin
from .models import *

# Register your models here.


class ActionCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'playerType', 'price', 'pressure')
    list_filter = ('playerType', 'price')
    search_fields = ('name', 'description')

class ReactionCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'playerType', 'price', 'type')
    list_filter = ('playerType', 'price', 'type')
    search_fields = ('name', 'description')

admin.site.register(ActionCard)
admin.site.register(ReactionCard)