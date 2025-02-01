from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Room, Player
from .serializers import RoomSerializer, PlayerSerializer

from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.db import transaction


class GetCsrfTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        token = get_token(request)
        return Response({'csrfToken': token})   

class CreateRoomView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        name = request.data.get('name')
        if not name:
            return Response({"detail": "Player name is required."}, status=status.HTTP_400_BAD_REQUEST)

        is_private = request.data.get('is_private', True)
        max_players = request.data.get('max_players', 14)

        if max_players > 14:
            return Response({"detail": "Maximum players can't exceed 14."}, status=status.HTTP_400_BAD_REQUEST)
        
        room = (
            Room.objects.create_private_room(max_players=max_players)
            if is_private else
            Room.objects.create_public_room(max_players=max_players)
        )
        
        player = Player.objects.create(name=name, room=room)
        room.current_players_count += 1
        room.save()
        
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class JoinRoomView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        name = request.data.get('name')
        unique_code = request.data.get('unique_code', None)
        room_type = request.data.get('type', 'public')

        if not name:
            return Response({"detail": "Player name is required."}, status=status.HTTP_400_BAD_REQUEST)

        room = None
        if unique_code:
            if room_type == "private":
                room = Room.objects.create_private_room(unique_code=unique_code)
                if not room:
                    return Response({"detail": "Can't use this unique code."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                room = Room.objects.get_private_room(unique_code=unique_code)
                
            if not room:
                return Response({"detail": f"Private room with code {unique_code} does not exist or is inactive."}, status=status.HTTP_404_NOT_FOUND)
            
            if Player.objects.filter(name=name, room=room).count() > 0:
                return Response({"detail": "Player with that name already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
            if room.current_players_count >= room.max_players:
                return Response({"detail": "Room is full."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            room = Room.objects.get_public_room()
            if not room or Player.objects.filter(room=room, name=name).exists():
                room = Room.objects.create_public_room()

        with transaction.atomic():
            player = Player.objects.create(name=name, room=room)
            room.current_players_count += 1

            room.save()
            
        player_serializer = PlayerSerializer(player)
        return Response(player_serializer.data, status=status.HTTP_200_OK)