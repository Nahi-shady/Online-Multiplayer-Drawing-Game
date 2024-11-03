from django.db import models
from django.shortcuts import get_object_or_404
from .managers import RoomManager

class Room(models.Model):
    is_private = models.BooleanField(default=True)
    unique_code = models.CharField(max_length=8, blank=True, null=True, unique=True)
    
    current_drawer = models.ForeignKey('Player', on_delete=models.SET_NULL, blank=True, null=True, related_name='drawer_room')
    current_players_count = models.IntegerField(default=0)
    current_word = models.CharField(default='', blank=True, null=False)
    score_pool = models.IntegerField(default=450, blank=True, null=False)
    
    max_players = models.IntegerField(default=14)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RoomManager()

    def set_next_drawer(self):
        players = list(self.players.filter(is_active=True).order_by('turn_order'))
        
        if players:
            if self.current_drawer and self.current_drawer in players:
                index = players.index(self.current_drawer)
                next_index = (index + 1) % len(players)
            else:
                next_index = 0
                
            self.current_drawer = players[next_index]
            self.save()
            
            return self.current_drawer
        else:
            self.current_drawer = None
            self.save()
    
    def __str__(self):
        return f"{'Private' if self.is_private else 'Public'} Room (ID: {self.id})"


class Player(models.Model):
    name = models.CharField(max_length=15, blank=False, null=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    turn_order = models.IntegerField(default=0)  # Player's turn order within the room
    is_active = models.BooleanField(default=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} in Room {self.room.id}"
