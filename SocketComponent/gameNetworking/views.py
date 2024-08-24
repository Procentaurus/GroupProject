from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import logging

from .permissions import IsAdmin
from .throttlers import GameAuthenticationTokenCreateHourRate

from .serializers import *


logger = logging.getLogger(__name__)


class GameAuthenticationTokenCreateView(generics.CreateAPIView):

    throttle_classes = [GameAuthenticationTokenCreateHourRate]
    permission_classes = [IsAuthenticated,]
    queryset = GameAuthenticationToken.objects.all()

    def get_output_serializer_class(self):
        if self.request.user.is_admin:
            return GameAuthenticationTokenAdminSerializer
        else:
            return GameAuthenticationTokenPublicSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        potential_tokens = GameAuthenticationToken.objects.filter(
            user_id=user.id)
        number_of_found_tokens = len(potential_tokens)

        if number_of_found_tokens == 0:
            token = GameAuthenticationToken.objects.create(user_id=user.id)
            serializer_class = self.get_output_serializer_class()
            dto = serializer_class(token).data
            return Response(dto, status=status.HTTP_201_CREATED)
        elif number_of_found_tokens > 1:
            logger.error(
                "Multiple game tokens connected to player %s",
                user.username)
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("You have already requested game token.",
                status=status.HTTP_400_BAD_REQUEST)


class GameAuthenticationTokenListView(generics.ListCreateAPIView):

    permission_classes = (IsAuthenticated & IsAdmin,)
    queryset = GameAuthenticationToken.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class GameAuthenticationTokenView(APIView):

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            view = GameAuthenticationTokenListView.as_view()
        elif request.method == 'POST':
            view = GameAuthenticationTokenCreateView.as_view()
        else:
            return Response(
                {'detail': 'Method not allowed'}, 
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return view(request, *args, **kwargs)
