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
        name = request.data.get('name')
        if not name:
            return Response({"detail": "Player name is required."}, status=status.HTTP_400_BAD_REQUEST)

        is_private = request.data.get('is_private', False)
        max_players = request.data.get('max_players', 14)

        if max_players > 14:
            return Response({"detail": "Maximum players can't exceed 14."}, status=status.HTTP_400_BAD_REQUEST)
        
        room = (
            Room.objects.create_private_room(max_players=max_players)
            if is_private else
            Room.objects.create_public_room(max_players=max_players)
        )
        
        player = Player.objects.create(name=name, room=room, turn_order=room.current_players_count)
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

        if not name:
            return Response({"detail": "Player name is required."}, status=status.HTTP_400_BAD_REQUEST)

        room = None
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
            player = Player.objects.create(name=name, room=room, turn_order=room.current_players_count)
            room.current_players_count += 1

            room.save()
            
        player_serializer = PlayerSerializer(player)
        return Response(player_serializer.data, status=status.HTTP_200_OK)

class LeaveRoomView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        player_id = request.data.get('player_id')
        if not player_id:
            return Response({"detail": "Player player_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        player = get_object_or_404(Player, id=player_id)
        room = player.room

            
        with transaction.atomic():
            if room.current_drawer == player:
                if room.current_players_count <= 1:
                    room.current_drawer = None
                else:
                    room.set_next_drawer()
                    
            player.delete()

            room.current_players_count -= 1
            if room.current_players_count <= 0:
                room.is_active = False  # Deactivate room if no players are left
            room.save()
            
        active_players = room.players.filter(is_active=True).order_by('turn_order')
        for i, player in enumerate(active_players):
            player.turn_order = i

        Player.objects.bulk_update(active_players, ['turn_order'])
    
        return Response({"detail": "Left room successfully."}, status=status.HTTP_200_OK)