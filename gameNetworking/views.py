from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from WebGame.permissions import *
from .serializers import *

class GameAuthenticationTokenList(generics.ListCreateAPIView):

    permission_classes = (IsAuthenticated & ((ChoseSafeMethod & IsAdmin ) | ~ChoseSafeMethod),)

    def get_serializer_class(self):
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
            dto = GameAuthenticationTokenPublicSerializer(token).data
            return Response(dto, status=status.HTTP_201_CREATED)
        
        elif number_of_found_tokens > 1:
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            return Response("You have already requested game token.", status=status.HTTP_400_BAD_REQUEST)