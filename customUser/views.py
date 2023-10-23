from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated

from .serializers import *
from WebGame.permissions import *


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
        

class MyUserList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated | ~ChoseSafeMethod)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MyUserCreateUpdateSerializer
        else:
            if self.request.user.is_admin:
                return MyUserAccountDataSerializer
            else:
                return MyUserPublicListSerializer
        
    def get_queryset(self):

        objects = MyUser.objects.all()
        
        username = self.request.query_params['username']
        if username:
            objects = objects.filter(username__icontains=username)
        
        return objects
    
    def perform_create(self, serializer):

        user = MyUser.objects.create_user(
            bleach.clean(serializer.validated_data.get('email')),
            bleach.clean(serializer.validated_data.get('username')),
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
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        dto = MyUserAccountDataSerializer(user).data
        
        return Response(dto, status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MyUserDetail(generics.RetrieveUpdateAPIView):

    permission_classes = (
        IsAuthenticated &
        ((IsTheVeryUser | IsAdmin) | ChoseSafeMethod)
        )

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return MyUserCreateUpdateSerializer
        else:
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_update(serializer)

        dto = MyUserAccountDataSerializer(user).data
        
        return Response(dto, status=status.HTTP_201_CREATED)


