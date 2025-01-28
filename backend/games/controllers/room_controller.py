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

class RoomControler():
    async def __init__(self, room_id: int) -> None:
        self.room_id = room_id
        self.room = await self.get_room()
        
        self.drawer = None
        self.players_count = self.room.current_players_count
        self.current_word = ''
        self.guess_count = 0
        self.turn_count = 0
        self.score_pool = 450
        self.on = False
    
    async def refresh_room_db(self) -> Room:
        self.room = await self.get_room()
        if self.room:
            self.drawer = None
            self.players_count = self.room.current_players_count
            self.current_word = self.room.current_word
            self.guess_count = self.room.guess_count
            self.turn_count = self.room.turn_count
            self.score_pool = self.room.score_pool
            self.on = self.room.on
            
            return self.room
        
    async def get_room(self) -> Room:
        try:
            return await sync_to_async(Room.objects.get)(id=self.room_id)
        except Room.DoesNotExist:
            logging.error('Room with id %s not found', self.room_id)
            return None
    
    async def get_drawer(self) -> Player:
        room = self.get_room()
        if room:
            drawer = await sync_to_async(lambda: room.current_drawer)()
            return drawer
        
        return False