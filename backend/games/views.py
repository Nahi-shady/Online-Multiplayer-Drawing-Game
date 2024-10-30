from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404

from .serializers import RoomModelSerializer

class RoomView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RoomModelSerializer(data=request.data)
        
        if serializer.is_valid():
            room = serializer.save()

            return Response({
                "message": "Room created successfully",
                "room": {
                    "id": room.id,
                    "is_private": room.is_private,
                    "unique_link": room.unique_link if room.is_private else None
                }
            }, status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

        