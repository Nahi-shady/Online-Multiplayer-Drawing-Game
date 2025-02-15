import random
import logging
from asgiref.sync import sync_to_async
import asyncio


from django.db.models import F

from ..models import Room, Player

class RoomController():
    def __init__(self, room_id: int) -> None:
        self.room_id = room_id
        self.room = None
        self.players = []
        self.drawer = None
        
        self.current_players_count = 0
        self.current_word = ''
        self.guess_count = 0
        self.turn_count = 0
        self.score_pool = 450
        self.on = False
    
    async def refresh_room_db(self, room=None) -> Room:
        self.room = await self.get_room()
        if self.room:
            self.players = await self.get_players_in_order()
            self.turn_count = self.room.turn_count
            self.players_count = self.room.current_players_count
            self.current_word = self.room.current_word
            self.guess_count = self.room.guess_count
            self.score_pool = self.room.score_pool
            self.on = self.room.on
            
            return self.room
        else:
            self.room = None
            self.drawer = None
            self.players = []
            self.on = False
        
        return None
    
    async def get_player(self, player_id: int) -> Player:
        try:
            return await sync_to_async(Player.objects.get)(id=player_id)
        except:
            # print('Player with id %s not found', player_id)
            return None
    
    async def get_room(self) -> Room:
        try:
            room = await sync_to_async(Room.objects.get)(id=self.room_id)
            self.refresh_room_db(room)
            return room
        except Room.DoesNotExist:
            # print('Room with id %s not found', self.room_id)
            return None
    
    async def get_drawer(self) -> Player:
        room = await self.get_room()
        if room:
            drawer = await sync_to_async(lambda: room.current_drawer)()
            self.drawer = drawer
            return self.drawer
        
        return None
    
    async def is_active(self) -> bool:
        room = self.room if self.room else await self.get_room()
        if not room or not room.is_active or room.current_players_count <= 0:
            return False
        
        return True
    
    async def remove_room(self) -> bool:
        room = self.room if self.room else await self.get_room()
        if room:
            await sync_to_async(room.delete)()
            return True
        
        return False  
    
    async def get_players_in_order(self) -> list:
        players = await sync_to_async(lambda: list(Player.objects.filter(room_id=self.room_id).order_by("joined_at")))()
        self.players = players
        
        return players
      
    async def correct_guess(self, player_id: int, guess: str) -> bool:
        player = await self.get_player(player_id)
        room = await self.get_room()
        current_drawer = await sync_to_async(lambda: room.current_drawer)()
        
        if not player or not room.on or not current_drawer or player_id == current_drawer.id or player.guessed or guess.lower() != room.current_word.lower():
            # print('guess not valid')
            return False
        
        player.score = F('score') + room.score_pool
        player.guessed = True
        await sync_to_async(player.save)()

        self.drawer.score = F('score') + (room.score_pool // room.current_players_count)
        await sync_to_async(self.drawer.save)()
        
        room.score_pool = F('score_pool') - 33
        room.guess_count = F('guess_count') + 1
        await sync_to_async(room.save)()
        await sync_to_async(room.refresh_from_db)()
        
        await self.refresh_room_db(room)
        return True
        
    async def word_chosen(self, word: str) -> bool:
        room = self.room if self.room else await self.get_room()
        if not room:
            # print('Could not save drawer word choice to db')
            return False
        
        room.current_word = word
        await sync_to_async(room.save)()
        
        self.current_word = word
        
        return True
    
    async def prepare_room_for_new_round(self) -> bool:
        room = self.room if self.room else await self.get_room()
        if not room or room.current_players_count <= 1:
            # print("Not enough players have joined")
            return False
        
        room.turn_count = 0
        room.on = True
        await sync_to_async(room.save)()
        
        self.refresh_room_db()
        
        return True
    
    async def room_is_ready(self) -> bool:
        room = self.room if self.room else await self.get_room()
        if not room:
            # print("Room doesn't exist")
            return False
        
        if room.turn_count >= room.max_turn:
            room.on = False
            self.on = False
            await sync_to_async(room.save)()
            
            # print("Last turn is played")
            return False
        
        return True
      
    async def set_next_drawer(self) -> bool:
        room = await self.get_room()
        players = await self.get_players_in_order()
        drawer = await sync_to_async(lambda: room.current_drawer)()
        
        if players:
            if drawer and drawer in players:
                index = players.index(drawer)
                next_index = (index + 1) % len(players)
                new_drawer = players[next_index]
            else:
                new_drawer = players[0]
        else:
            # print("Couldn't set drawer for turn")
            return False
        
        if new_drawer:
            room.current_drawer = new_drawer
            self.drawer = new_drawer
            await sync_to_async(room.save)()
            
            # print(f"Drawer: {self.drawer.name}")
        
            return True
    
    async def reset_room_for_new_turn(self) -> bool:
        room = await self.get_room()
        try:
            room.turn_count = F('turn_count') + 1
            room.score_pool = 450
            room.guess_count = 0
            room.current_word = ''
            
            await sync_to_async(room.save)()
            await sync_to_async(room.refresh_from_db)()
        except:
            # print("Couldn't reset room for new turn")
            return False  
              
        await self.refresh_room_db(room)
        
        # print(f"Turn {self.turn_count}")
        
        return True
