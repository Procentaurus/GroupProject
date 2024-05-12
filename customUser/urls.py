from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path

from .views import *

urlpatterns = [
    # Endpoint for getting both access amd refresh tokens
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain'),
    
    # Endpoint for getting new access token with refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Default endpoint with users' list
    path('', MyUserList.as_view(), name='user_list'),

    # Enpoint with data of single user
    path('<str:id>/', MyUserDetail.as_view(), name='user'),

    # Endpoint with already finished games
    path('archives/', GameArchiveList.as_view(), name='archive_list')
]
