from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

from WebGame.permissions import *
from .serializers import *


logger = logging.getLogger(__name__)

class GameAuthenticationTokenList(generics.ListCreateAPIView):

    permission_classes = (
        IsAuthenticated & ((ChoseGetMethod & IsAdmin ) | ChosePostMethod),
    )

    def get_output_serializer_class(self):
        if self.request.user.is_admin:
            return GameAuthenticationTokenAdminSerializer
        else:
            return GameAuthenticationTokenPublicSerializer

    def get_queryset(self):
        objects = GameAuthenticationToken.objects.all()
        return objects

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):

        user = request.user
        potential_tokens = GameAuthenticationToken.objects.filter(user=user)
        number_of_found_tokens = len(potential_tokens)

        if number_of_found_tokens == 0:
            token = GameAuthenticationToken.objects.create(user=user)

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
