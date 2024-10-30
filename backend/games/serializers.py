from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from .models import Room, Player

class RoomModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['is_private']
        
    def create(self, data):
        room = Room.objects.create_room(is_private=data['is_private'])
        
        return room