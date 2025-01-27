import json
import random
import logging
from asgiref.sync import sync_to_async
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection

from django.db.models import F

from .models import Room, Player
from .word_pool import EASY_WORDS, HARD_WORDS, FUN

class GameController():
    async def __init__(self, room_id):
        self.room_id = room_id
        self.room_group_name = f'room_{self.room_id}'
        
    async def player_joined(self, player_id: int) -> None:
        try:
            player = await sync_to_async(Player.objects.get)(pk=player_id)
            player.is_active = True
            await player.save()
        except Player.DoesNotExist:
            logging.error(f'Player with id {player_id} does not exist.')
            return
        
        await self.group_send(
            {
                'type': 'player_joined',
                'player_id': player_id
            })