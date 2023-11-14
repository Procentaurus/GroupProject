from django.urls import path

from .views import *

urlpatterns = [
    path('game_token/', GameAuthenticationTokenList.as_view(), name='game_token_obtain'),
]