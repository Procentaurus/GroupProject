from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate

from .serializers import *


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):

        email = bleach.clean(request.data.get('email'))
        password = request.data.get('password')

        if email and password:

            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if user:
                response = super().post(request, *args, **kwargs)
                if response.status_code == 200:
                    # You can perform additional actions here, e.g., logging the login.
                    return response

            return Response({'detail': 'Invalid email or password'}, status=400)
