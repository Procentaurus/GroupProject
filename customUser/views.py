from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated

import bleach

from .serializers import *
from WebGame.permissions import *


class CustomTokenObtainPairView(TokenObtainPairView): # implementation of endpoint enabling getting of both access and refresh tokens

    def post(self, request, *args, **kwargs):

        email = None if request.data.get('email') is None else bleach.clean(request.data.get('email'))
        password = request.data.get('password')

        if email and password:

            user = authenticate(email=email, password=password)
            if user:
                response = super().post(request, *args, **kwargs)
                if response.status_code == 200:
                    # You can perform additional actions here, e.g., logging the login.
                    return response

            return Response({'detail': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Lacking obligatory credentials: email or password.'}, status=status.HTTP_400_BAD_REQUEST)
        

class MyUserList(generics.ListCreateAPIView): # implementation of CRUD enpoints for MyUser class i.e.
    
    permission_classes = (IsAuthenticated | (~ChoseSafeMethod),)  # calculating adequate permissions

    def get_serializer_class(self): # choosing adequate serializer 
        if self.request.method == 'POST':
            return MyUserCreateUpdateSerializer
        else:
            return MyUserPublicGetSerializer
        
    def get_queryset(self): # filtering objects returned for GET many users endpoint
        objects = MyUser.objects.all()
        
        username = self.request.query_params.get('username', None)
        if username is not None:
            objects = objects.filter(username__icontains=username)
        
        return objects
    
    def perform_create(self, serializer): # customized creation of MyUser entity

        user = MyUser.objects.create_user(
            bleach.clean(serializer.validated_data.get('email')),  # filtering possible script injections
            bleach.clean(serializer.validated_data.get('username')), # filtering possible script injections
            serializer.validated_data.get('password')
        )

        if serializer.validated_data.get('phoneNumber') is not None:
            user.phone_number = serializer.validated_data.get('phoneNumber')

        if serializer.validated_data.get('hide_contact_data') is not None:
            user.hide_contact_data = serializer.validated_data.get('hide_contact_data')

        user.save()
        return user

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        valid_data = serializer.is_valid()

        if valid_data:
            user = self.perform_create(serializer)
            dto = MyUserAdminSerializer(user).data if request.user.is_admin else MyUserAccountDataSerializer(user).data
            return Response(dto, status=status.HTTP_201_CREATED)
        else:
            return Response("Passed invalid data", status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MyUserDetail(generics.RetrieveUpdateAPIView):

    permission_classes = ( # calculating adequate permissions
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
            
    def get_outpu_serializer_class(self):
        if self.request.user.id == self.get_object().id:
            return MyUserAccountDataSerializer
        else:
            return MyUserPublicDetailSerializer
            
    def perform_update(self, serializer):  # customized update of MyUser entity
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

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        is_valid = serializer.is_valid()

        if is_valid:
            user = self.perform_update(serializer)
            dto = MyUserAccountDataSerializer(user).data
            return Response(dto, status=status.HTTP_201_CREATED)
        else:
            return Response("Passed invalid data", status=status.HTTP_400_BAD_REQUEST)

