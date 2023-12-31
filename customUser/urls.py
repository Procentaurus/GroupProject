from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path

from .views import *

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), # endpoint for getting both access amd refresh tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # endpoint for getting new access token with refresh token

    path('', MyUserList.as_view(), name='user_list'), # default endpoint with users' list 
    path('<str:id>/', MyUserDetail.as_view(), name='user'), # enpoint with data of single user
]