from django.urls import path

from .views import GameAuthenticationTokenView


urlpatterns = [
    path('game_token/', GameAuthenticationTokenView.as_view(),
        name='game_token_obtain'),
]
