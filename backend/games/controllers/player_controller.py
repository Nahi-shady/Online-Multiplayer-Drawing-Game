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
    async def player_joined(self, player_id: int) -> bool:
        try:
            player = await self.get_player(player_id)
            player.is_active = True
            await player.save()
        except Player.DoesNotExist:
            logging.error(f'Player with id {player_id} does not exist.')
            return None
        return True
    
    async def remove_player(self, player_id: int) -> bool:
        try:
            player, room = await self.get_player(player_id), await sync_to_async(Room.objects.get)(id=self.room_id)
            if not player:
                raise Player.DoesNotExist(player_id)
            if not room:
                raise Room.DoesNotExist(self.room_id)
            
            room.current_players_count = F('current_players_count') - 1
            await sync_to_async(room.save)()
            
            await sync_to_async(player.delete)()
        except Player.DoesNotExist:
            logging.error(f'Player with id {player_id} does not exist.')
            return False
        except Room.DoesNotExist:
            logging.error(f'Room with id {player_id} does not exist.')
            return False
        
        return True