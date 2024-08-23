from django.urls import path

from .views import *

urlpatterns = [
    # Default endpoint with users' list
    path('',
         MyUserView.as_view(),
         name='user_list'),

    # Endpoint for getting both access amd refresh tokens
    path('token/',
         CustomTokenObtainPairView.as_view(),
         name='token_obtain'),
    
    # Endpoint for getting new access token with refresh token
    path('token/refresh/',
         CustomTokenRefreshView.as_view(),
         name='token_refresh'),

    # Enpoint with data of single user
    path('<str:id>/',
         MyUserDetailView.as_view(),
         name='user'),

    # Endpoint with already finished games
    path('api/archives/',
         GameArchiveList.as_view(),
         name='archive_list'),
]
