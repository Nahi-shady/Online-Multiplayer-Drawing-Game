from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string

class RoomManager(BaseUserManager):
    def create_room(self, is_private):
        room = self.model(is_private=is_private)
        if is_private:
            room.unique_link = f"http://127.0.0.1:8000/games/room/{get_random_string(16)}"
        room.save()
        
        return room