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
            self.drawer = self.room.current_drawer
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
        room = await self.get_room()
        if room:
            drawer = await sync_to_async(lambda: room.current_drawer)()
            self.drawer = drawer
            return self.drawer
        
        return False
    
    
    async def update_scores(self, player_id: int, guess: str) -> bool:
        player = self.get_player(player_id)
        if not self.on or player_id == self.drawer.id or player.guessed or guess.lower() != self.current_word.lower():
            return False
        
        player.score = F('score') + self.room.score_pool
        player.guessed = True
        await sync_to_async(player.save)()

        self.drawer.score = F('score') + (self.room.score_pool // self.room.current_players_count)
        await sync_to_async(self.drawer.save)()
        
        self.room.score_pool = F('score_pool') - 33
        self.room.guess_count = F('guess_count') + 1
        await sync_to_async(self.room.save)()
        await sync_to_async(self.room.refresh_from_db)()
        
        await self.refresh_room_db()
        return True
        
    async def word_chosen(self, word: str) -> bool:
        room = self.get_room()
        if room:
            room.current_word = word
            await sync_to_async(room.save)()
            
            self.current_word = word
            return True
        else:
            logging.error('Could not save drawer word choice to db')
            return False
        
    async def is_active(self) -> bool:
        room = await self.get_room()
        if not room or not room.is_active or room.current_players_count <= 0:
            return False
        
        return True
    
    async def remove_room(self) -> bool:
        room = await self.get_room()
        if room:
            await sync_to_async(room.delete)()
            return True
        
        return False