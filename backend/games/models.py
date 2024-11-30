from asgiref.sync import sync_to_async

from django.db import models
from django.shortcuts import get_object_or_404

from .managers import RoomManager

class Room(models.Model):
    is_private = models.BooleanField(default=True)
    unique_code = models.CharField(max_length=8, blank=True, null=True, unique=True)
    
    current_drawer = models.ForeignKey('Player', on_delete=models.SET_NULL, blank=True, null=True, related_name='drawer_room')
    current_players_count = models.IntegerField(default=0)
    current_word = models.CharField(default='illustra', blank=True, null=False)
    score_pool = models.IntegerField(default=450, blank=True, null=False)
    turn_count = models.IntegerField(default=0, blank=False, null=False)
    guess_count = models.IntegerField(default=0, blank=False, null=False)
    on = models.BooleanField(default=False)
    
    max_players = models.IntegerField(default=14)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RoomManager()       
    
    def __str__(self):
        return f"{'Private' if self.is_private else 'Public'} Room (ID: {self.id})"


class Player(models.Model):
    name = models.CharField(max_length=15, blank=False, null=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    
    score = models.IntegerField(default=0)
    guessed = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    joined_at = models.DateField(auto_now_add=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'score': self.score}
    
    def __str__(self):
        return f"{self.name} in Room {self.room.id}"