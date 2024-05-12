from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('gameApi.urls')),
    path('game/', include('gameNetworking.urls')),
    path('users/', include('customUser.urls'))
]
