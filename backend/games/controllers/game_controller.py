import json
import random
import logging
from asgiref.sync import sync_to_async
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from channels.layers import get_channel_layer

from .player_controller import PlayerController
from .room_controller import RoomController

from .word_pool import EASY_WORDS, HARD_WORDS, FUN

channel_layer = get_channel_layer()

room_task = {}

class GameController():
    async def __init__(self, room_id):
        self.room_id = room_id
        self.room_group_name = f'room_{self.room_id}'
        
        self.player_controller = PlayerController(self.room_id)
        self.room_controller = RoomController(self.room_id)
        
    async def player_joined(self, player_id: int) -> bool:
        if self.player_controller.player_joined(player_id):
            await sync_to_async(channel_layer.group_send)(
                self.room_group_name, {
                    'type': 'player_joined',
                    'player_id': player_id
                }
            )
            return True
        return False
    async def player_left(self, player_id: int) -> bool:
        player = await self.player_controller.get_player(player_id)
        drawer = await self.room_controller.get_drawer(player_id)
        
        if player and drawer and player == drawer:
            await sync_to_async(channel_layer.group_send)(
                self.room_group_name, {
                    "type": "skip_turn",
                 "message": "Drawer disconnected!"
                })
            
            if self.room_id in room_task:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "message", "message": "Drawer disconnected"}
                )
                
                room_task[self.room_id].cancel()
                del room_task[self.room_id]
            else:
                await self.channel_layer.group_send(
                self.room_group_name,
                    {"type": "message",
                    "message": "not handled drawer leave!"}
                )

        
        if await self.player_controller.remove_player(player_id):
            await sync_to_async(channel_layer.group_send)(
                self.room_group_name,{
                    'type': 'player_left',
                    'player_id': player_id
                })
        
        if not await self.room_controller.is_active():
            if self.room_id in room_task:
                room_task[self.room_id].cancel()
                del room_task[self.room_id]
            
            if not await self.room_controller.remove_room():
                logging.info("Room was not removed")
        
        return True