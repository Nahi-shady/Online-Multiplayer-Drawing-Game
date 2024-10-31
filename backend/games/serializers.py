# serializers.py

from rest_framework import serializers
from .models import Room, Player

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'is_private', 'unique_code', 'current_players_count', 'max_players', 'is_active']


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'room', 'turn_order', 'is_active', 'score']
