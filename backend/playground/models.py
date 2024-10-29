from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):

    is_private = models.BooleanField(default=True)
    unique_link = models.URLField(blank=True, null=True)  # For private rooms
    max_players = models.IntegerField(default=14)
    current_players_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room_type.capitalize()} Room (ID: {self.id})"

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to Django's built-in User model
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    turn_order = models.IntegerField()  # Order in which the player takes their turn
    is_active = models.BooleanField(default=True)  # To track if the player is currently in the game
    score = models.IntegerField(default=0)  # Track player score

    def __str__(self):
        return f"{self.user.username} in Room {self.room.id}"
