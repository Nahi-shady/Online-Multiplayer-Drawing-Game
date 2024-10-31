from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import Room, Player
from .serializers import RoomSerializer, PlayerSerializer

from django.shortcuts import get_object_or_404
from django.db import transaction

class CreateRoomView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        is_private = request.data.get('is_private', False)
        max_players = request.data.get('max_players', 14)

        if is_private:
            room = Room.objects.create_private_room(max_players=max_players)
        else:
            room = Room.objects.create_public_room(max_players=max_players)
        
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class JoinRoomView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        name = request.data.get('name')
        unique_code = request.data.get('unique_code', None)

        if not name:
            return Response({"detail": "Player name is required."}, status=status.HTTP_400_BAD_REQUEST)

        if unique_code:
            room = Room.objects.get_private_room(unique_code=unique_code)
            if not room:
                return Response({"detail": "Private room with this code does not exist or is inactive."}, status=status.HTTP_404_NOT_FOUND)
            if room.current_players_count >= room.max_players:
                return Response({"detail": "Room is full."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            room = Room.objects.get_public_room()
            if not room:
                return Response({"detail": "No public rooms available."}, status=status.HTTP_404_NOT_FOUND)
        
        
        with transaction.atomic():
            room.current_players_count += 1
            room.save()

            player = Player.objects.create(name=name, room=room, turn_order=room.current_players_count)
            player_serializer = PlayerSerializer(player)

        return Response(player_serializer.data, status=status.HTTP_200_OK)

class LeaveRoomView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request, room_id):
        name = request.data.get('name')
        if not name:
            return Response({"detail": "Player name is required."}, status=status.HTTP_400_BAD_REQUEST)

        room = get_object_or_404(Room, id=room_id, is_active=True)
        player = get_object_or_404(Player, name=name, room=room)

        with transaction.atomic():
            player.is_active = False
            player.save()

            room.current_players_count -= 1
            if room.current_players_count <= 0:
                room.is_active = False  # Deactivate room if no players are left
            room.save()

        return Response({"detail": "Left room successfully."}, status=status.HTTP_200_OK)