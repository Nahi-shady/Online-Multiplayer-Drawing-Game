import json
import random
import logging
from asgiref.sync import sync_to_async
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection

from .player_controller import PlayerController
from .room_controller import RoomController

from .word_pool import EASY_WORDS, HARD_WORDS, FUN

class GameController():
    async def __init__(self, room_id):
        self.room_id = room_id
        self.room_group_name = f'room_{self.room_id}'
        
        self.player_controller = PlayerController(self.room_id)
        self.room_controller = RoomController(self.room_id)
        
    async def player_joined(self, player_id: int) -> bool:
        if self.player_controller.player_joined(player_id):
            await self.group_send(
                {
                    'type': 'player_joined',
                    'player_id': player_id
                })
            return True
        return False
    async def player_left(self, player_id: int) -> bool:
        if self.player_controller.remove_player(player_id):
            await self.group_send(
                {
                    'type': 'player_left',
                    'player_id': player_id
                })
            
            return True
        
        return False