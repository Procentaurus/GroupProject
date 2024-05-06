from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import bleach

from WebGame.permissions import *

from .serializers import *
from .user_update import *
from .response_decryptor import AESDecryptor
from .models import MyUser


class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        # decryptor = AESDecryptor(
        #     settings.AES_SECRET_KEY,
        #     settings.AES_IV
        # )
        # decrypted_msg = decryptor.decrypt(request.data)
        # email, password = self._retrieve_login_data(decrypted_msg)

        email = bleach.clean(request.data.get('email'))
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'detail': 'Lacking required credentials: email or password.'},
                status=status.HTTP_400_BAD_REQUEST)

        #TODO Logging
        email = email.lower()
        return super().post(request, *args, **kwargs)
        
    def _retrieve_login_data(self, data):
        # Email and password are divided with '+' sign
        plus_index = data.find('+')
        if plus_index != -1:
            return bleach.clean(data[:plus_index]), data[(plus_index + 1):]
        else:
            return None, None

class MyUserList(generics.ListCreateAPIView):
    
    permission_classes = (
        IsAuthenticated | (~ChoseSafeMethod),
    )

    # Choose dto for incoming data
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MyUserCreateUpdateSerializer
        else:
            return MyUserPublicGetSerializer

    def get_output_serializer_class(self):
        user = self.request.user
        if user.is_anonymous:
            return MyUserAccountDataSerializer
        elif self.request.user.is_admin:
            return MyUserAdminSerializer
        else:
            return MyUserAccountDataSerializer

    def get_queryset(self):
        objects = MyUser.objects.all()
        username = self.request.query_params.get('username', None)
        in_game = self.request.query_params.get('in_game', None)
        
        if username is not None:
            objects = objects.filter(username__icontains=username)
        if in_game is not None:
            objects = objects.filter(in_game=in_game)

        return objects
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        user = self.perform_create(serializer)
        dto = self.serialize_resp_body(user)
        return Response(dto, status=status.HTTP_201_CREATED)

    def serialize_resp_body(self, user):
        serializer_class = self.get_output_serializer_class()
        dto = serializer_class(user).data
        return dto
        
    def perform_create(self, serializer):
        data = serializer.validated_data
        user = MyUser.objects.create_user(
            data.get('email'),
            data.get('username'),
            data.get('password')
        )
        update_bio(data, user)
        update_hide_contact_data(data, user)
        update_phone_number(data, user)

        user.save()
        return user


class MyUserDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (
        IsAuthenticated &
        (
            (IsTheVeryUser | IsAdmin) | ChoseSafeMethod
        ),
    )
    queryset = MyUser.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        return MyUserCreateUpdateSerializer


    def get_output_serializer_class(self):
        if self.request.user.id == self.get_object().id:
            return MyUserAccountDataSerializer
        else:
            return MyUserPublicDetailSerializer

    def perform_update(self, serializer):
        user = self.get_object()
        data = serializer.validated_data

        update_email(data, user)
        update_username(data, user)
        update_bio(data, user)
        update_hide_contact_data(data, user)
        update_phone_number(data, user)

        user.save()
        return user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        dto = self.serialize_resp_body(user)
        return Response(dto, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        user = self.perform_update(serializer)
        dto = self.serialize_resp_body(user)
        return Response(dto, status=status.HTTP_201_CREATED)

    def serialize_resp_body(self, user):
        serializer_class = self.get_output_serializer_class()
        dto = serializer_class(user).data
        return dto
