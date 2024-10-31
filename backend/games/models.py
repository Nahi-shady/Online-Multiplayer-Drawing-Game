from django.db import models
from .managers import RoomManager

class Room(models.Model):
    is_private = models.BooleanField(default=True)
    unique_code = models.CharField(max_length=8, blank=True, null=True, unique=True)
    current_players_count = models.IntegerField(default=0)
    max_players = models.IntegerField(default=14)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RoomManager()

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
