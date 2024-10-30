from django.db import models
from users.models import User
from .managers import RoomManager
class Room(models.Model):

    is_private = models.BooleanField(default=True)
    unique_link = models.URLField(blank=True, null=True)
    current_players_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RoomManager()

    def __str__(self):
        return f"{'Private' if self.is_private else 'Public'} Room (ID: {self.id})"

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    turn_order = models.IntegerField()  # Order in which the player takes their turn
    is_active = models.BooleanField(default=True)  # To track if the player is currently in the game
    score = models.IntegerField(default=0)  # Track player score

    def __str__(self):
        return f"{self.user.username} in Room {self.room.id}"
