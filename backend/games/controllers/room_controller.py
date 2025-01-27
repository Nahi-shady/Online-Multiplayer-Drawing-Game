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
    def __init__(self, room_id: int) -> None:
        self.room_id = room_id
        self.room = await self.get_room()
        
        self.drawer = None
        self.players_count = self.room.current_players_count
        self.current_word = ''
        self.guess_count = 0
        self.turn_count = 0
        self.score_pool = 450
        self.on = False
        