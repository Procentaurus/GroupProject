from django.contrib import admin
from .models import *

# Register your models here.


class ActionCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'playerType', 'cost', 'pressure')
    list_filter = ('playerType', 'cost')
    search_fields = ('name', 'description')

class ReactionCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'playerType', 'cost', 'type')
    list_filter = ('playerType', 'cost', 'type')
    search_fields = ('name', 'description')

admin.site.register(ActionCard)
admin.site.register(ReactionCard)