from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path

from .views import *

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('/', MyUserList.as_view(), name='user_list'),
    path('/<str:id>/', MyUserDetail.as_view(), name='user'),
]