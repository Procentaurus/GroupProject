from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
import bleach

from .permissions import *
from .paginators import *
from .throttlers import *
from .archive_filter import *
from .serializers import *
from .user_update import *
from .models.my_user.my_user import MyUser
from .models.game_archive.game_archive import GameArchive
from .models.active_token.active_token import ActiveToken


class CustomTokenRefreshView(TokenRefreshView):

    serializer_class = EnhancedTokenRefreshSerializer
    throttle_classes = [
        CustomTokenRotateDayRate, CustomTokenRotateHourRate]

    def post(self, request, *args, **kwargs):
        self._refresh_token = request.data.get('refresh')

        resp = self._verify_token_is_send()
        if resp is None:
            resp = self._verify_is_token_valid()

        if resp is not None:
            return resp

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            active_token = ActiveToken.objects.get(token=self._refresh_token)
            active_token.delete()
            new_refresh_token = response.data.get('refresh')
            ActiveToken.objects.create(user=active_token.user,
                                       token=new_refresh_token)
        return response

    def _verify_token_is_send(self):
        if not self._refresh_token:
            return Response({'detail': 'Refresh token not provided'},
                            status=status.HTTP_400_BAD_REQUEST)
        else: return None
    
    def _verify_is_token_valid(self):
        try:
            _ = ActiveToken.objects.get(token=self._refresh_token)
            return None
        except:
            return Response({'detail': 'Invalid or expired refresh token'},
                            status=status.HTTP_401_UNAUTHORIZED)


class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = EnhancedTokenObtainPairSerializer
    throttle_classes = [
        CustomTokenCreateHourRate, CustomTokenCreateAnonHourRate]

    def post(self, request, *args, **kwargs):
        email = bleach.clean(request.data.get('email'))
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'detail': 'Lacking required credentials: email or password.'},
                status=status.HTTP_400_BAD_REQUEST)

        resp = self._verify_user_credentials(email.lower(), password)
        if resp: return resp

        user = MyUser.objects.get(email=email)
        self._remove_old_token(user)

        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            refresh_token = response.data.get('refresh')
            ActiveToken.objects.create(user=user, token=refresh_token)
        return response

    def _retrieve_login_data(self, data):
        # Email and password are divided with '+'
        plus_index = data.find('+')
        if plus_index != -1:
            return bleach.clean(data[:plus_index]), data[(plus_index + 1):]
        else:
            return None, None

    def _verify_user_credentials(self, email, password):
        try:
            user = MyUser.objects.get(email=email)
            if user is not None:
                if user.check_password(password):
                    return None
            raise MyUser.DoesNotExist
        except MyUser.DoesNotExist:
            return Response(
                {'detail': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
    def _remove_old_token(self, user):
        try:
            active_token = ActiveToken.objects.get(user=user)
            active_token.delete()
        except ActiveToken.DoesNotExist:
            pass


class MyUserCreateView(generics.CreateAPIView):

    throttle_classes = [MyUserCreateThrottleDayRate]

    def get_output_serializer_class(self):
        return MyUserGetDetailPrivateSerializer

    # Choose dto for incoming data
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MyUserCreateUpdateSerializer

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

class MyUserListView(generics.ListAPIView):

    pagination_class = MyUserPaginator
    permission_classes = [IsAuthenticated,]
    throttle_classes = [MyUserListThrottleDayRate,
                        MyUserListThrottleMinRate]

    def get_output_serializer_class(self):
        return MyUserGetAllSerializer

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
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_output_serializer_class()(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_output_serializer_class()(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyUserRetrieveView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated,]
    throttle_classes = [MyUserGetThrottleDayRate,
                        MyUserGetThrottleMinRate]
    lookup_field = 'id'
    queryset = MyUser.objects.all()

    def get_output_serializer_class(self):
        if self.request.user.id == self.get_object().id:
            return MyUserGetDetailPrivateSerializer
        elif self.request.user.is_admin:
            return MyUserAdminSerializer
        else:
            return MyUserGetDetailSerializer

    def get_output_serializer_class(self):
        if self.request.user.id == self.get_object().id:
            return MyUserGetDetailPrivateSerializer
        elif self.request.user.is_admin:
            return MyUserAdminSerializer
        else:
            return MyUserGetDetailSerializer

    def serialize_resp_body(self, user):
        serializer_class = self.get_output_serializer_class()
        dto = serializer_class(user).data
        return dto

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        dto = self.serialize_resp_body(user)
        return Response(dto, status=status.HTTP_200_OK)


class MyUserUpdateView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated & (AccessHisData | IsAdmin),]
    throttle_classes = [MyUserUpdateThrottleDayRate]
    lookup_field = 'id'
    queryset = MyUser.objects.all()

    def get_serializer_class(self):
        return MyUserCreateUpdateSerializer

    def get_output_serializer_class(self):
        if self.request.user.is_admin:
            return MyUserAdminSerializer
        else:
            return MyUserGetDetailPrivateSerializer

    def serialize_resp_body(self, user):
        serializer_class = self.get_output_serializer_class()
        dto = serializer_class(user).data
        return dto

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

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        user = self.perform_update(serializer)
        dto = self.serialize_resp_body(user)
        return Response(dto, status=status.HTTP_201_CREATED)


class MyUserDeleteView(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated & (AccessHisData | IsAdmin),]
    throttle_classes = [MyUserDeleteThrottleDayRate]
    lookup_field = 'id'
    queryset = MyUser.objects.all()

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class GameArchiveList(generics.ListAPIView):

    pagination_class = GameArchivePaginator
    permission_classes = [IsAuthenticated,]
    throttle_classes = [
        ArchiveListThrottleMinRate, ArchiveListThrottleDayRate]

    def get_serializer_class(self):
        return GameArchiveGetAllSerializer

    def get_queryset(self):
        objects = GameArchive.objects.all()
        username = self.request.query_params.get('username', None)
        date = self.request.query_params.get('start_date', None)
        length = self.request.query_params.get('length', None)
        winner = self.request.query_params.get('winner', None)
        objects = filter_by_date(objects, date)
        objects = filter_by_length(objects, length)
        objects = filter_by_winner(objects, winner)
        objects = filter_by_username(objects, username)
        return objects

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MyUserView(APIView):

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            view = MyUserListView.as_view()
        elif request.method == 'POST':
            view = MyUserCreateView.as_view()
        else:
            return Response(
                {'detail': 'Method not allowed'}, 
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return view(request, *args, **kwargs)


class MyUserDetailView(APIView):

    def dispatch(self, request, *args, **kwargs):
        view = None
        if request.method == 'GET':
            view = MyUserRetrieveView.as_view()
        elif request.method == 'PUT':
            view = MyUserUpdateView.as_view()
        elif request.method == 'DELETE':
            view = MyUserDeleteView.as_view()
        else:
            return Response(
                {'detail': 'Method not allowed'}, 
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return view(request, *args, **kwargs)
