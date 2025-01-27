import json
import random
import logging
from asgiref.sync import sync_to_async
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection

from django.db.models import F

from .models import Room, Player

class PlayerController():
    async def __init__(self, room_id: int) -> None:
        self.room_id = room_id
    
    async def get_player(self, player_id: int) -> Player:
        try:
            return await sync_to_async(Player.objects.get)(id=player_id)
        except:
            logging.error('Player with id %s not found', player_id)
            return None
    