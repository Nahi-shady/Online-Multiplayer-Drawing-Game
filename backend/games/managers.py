from django.db import models
from django.utils.crypto import get_random_string

class RoomManager(models.Manager):
    def create_private_room(self, unique_code, max_players=7):
        if not self.get_private_room(unique_code):
            return self.create(is_private=True, unique_code=unique_code, max_players=max_players)

    def create_public_room(self, max_players=7):
        return self.create(is_private=False, max_players=max_players)

    def get_public_room(self):
        # Find the first active public room that has space for more players
        return self.filter(is_private=False, is_active=True).exclude(current_players_count__gte=models.F('max_players')).first()

    def get_private_room(self, unique_code):
        room = self.filter(is_private=True, unique_code=unique_code, is_active=True).first()
        return room 