from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated

import bleach

from .serializers import *
from WebGame.permissions import *


class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):

        email = bleach.clean(request.data.get('email'))
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'detail': 'Lacking required credentials: email or password.'},
                status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)
        if not user:
            return Response(
                {'detail': 'Invalid email or password'},
                status=status.HTTP_400_BAD_REQUEST)
        
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            #TODO Logging
            return response


class MyUserList(generics.ListCreateAPIView):
    
    permission_classes = (IsAuthenticated | (~ChoseSafeMethod),)

    # Choose dto for incoming data
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MyUserCreateUpdateSerializer
        else:
            return MyUserPublicGetSerializer

    def get_output_serializer_class(self):
        if self.request.user.is_admin:
            return MyUserAdminSerializer
        else:
            return MyUserAccountDataSerializer
    
    # Filter queryset objects
    def get_queryset(self):
        objects = MyUser.objects.all()
        
        username = self.request.query_params.get('username', None)
        if username is not None:
            objects = objects.filter(username__icontains=username)
        
        return objects
    
    def perform_create(self, serializer):
        data = serializer.validated_data
        user = MyUser.objects.create_user(
            data.get('email'),
            data.get('username'),
            data.get('password')
        )

        if data.get('phoneNumber') is not None:
            user.phone_number = data.get('phoneNumber')

        if data.get('hide_contact_data') is not None:
            user.hide_contact_data = data.get('hide_contact_data')

        if data.get('bio') is not None:
            user.bio = data.get('bio')

        user.save()
        return user

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = self.perform_create(serializer)
            dto = None

            serializer_class = self.get_output_serializer_class()
            dto = serializer_class(user).data
            return Response(dto, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MyUserDetail(generics.RetrieveUpdateAPIView):

    permission_classes = (
        IsAuthenticated &
        ((IsTheVeryUser | IsAdmin) | ChoseSafeMethod),
    )

    queryset = MyUser.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return MyUserCreateUpdateSerializer
        else:
            return MyUserPublicGetSerializer

    def get_output_serializer_class(self):
        if self.request.user.id == self.get_object().id:
            return MyUserAccountDataSerializer
        else:
            return MyUserPublicDetailSerializer
            
    def perform_update(self, serializer):
        instance = self.get_object()

        email = serializer.validated_data.get("email")
        if email:
            instance.email = bleach.clean(email)

        username = serializer.validated_data.get("username")
        if username:
            instance.username = bleach.clean(username)

        phone_number = serializer.validated_data.get('phone_number')
        if phone_number is not None:
            instance.phone_number = phone_number

        hide_contact_data = serializer.validated_data.get('hide_contact_data')
        if hide_contact_data is not None:
            instance.hide_contact_data = hide_contact_data

        instance.save()
        return instance


    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)

        if serializer.is_valid():
            user = self.perform_update(serializer)
            serializer_class = self.get_output_serializer_class()
            dto = serializer_class(user).data
            return Response(dto, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
