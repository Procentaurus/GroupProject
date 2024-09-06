from django.urls import path

from .views import *

urlpatterns = [
    # Default endpoint with users' list
    path('users/',
         MyUserView.as_view(),
         name='user_list'),

    # Enpoint with data of single user
    path('users/<str:id>/',
         MyUserDetailView.as_view(),
         name='user'),

     # Endpoint for getting both access amd refresh tokens
    path('tokens/',
         CustomTokenObtainPairView.as_view(),
         name='token_obtain'),
    
    # Endpoint for getting new access token with refresh token
    path('tokens/refresh/',
         CustomTokenRefreshView.as_view(),
         name='token_refresh'),

    # Endpoint with already finished games
    path('archives/',
         GameArchiveList.as_view(),
         name='archive_list'),
]
