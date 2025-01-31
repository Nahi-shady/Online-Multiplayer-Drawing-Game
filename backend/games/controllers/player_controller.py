import random
import logging

from asgiref.sync import sync_to_async
import asyncio

from django.db.models import F

from ..models import Room, Player

class PlayerController():
    def __init__(self, room_id: int) -> None:
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
            if player.room.id != self.room_id:
                return False
            
            player.is_active = True
            await player.save()
        except Player.DoesNotExist:
            logging.error(f'Player with id {player_id} does not exist.')
            return False
        
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
    
    async def get_players_in_order(self) -> list:
        return await sync_to_async(lambda: list(Player.objects.filter(room_id=self.room_id).order_by("joined_at")))()

    async def get_scoreboard(self) -> list:
        players = await sync_to_async(lambda: list(Player.objects.filter(room_id=self.room_id).order_by("score")))()

        return [{"name": player.name, "score":player.score} for player in players]
        
    async def reset_player_scores(self) -> bool:
        players = await self.get_players_in_order()
        if not players:
            return False

        for player in players:
            player.score = 0

        await sync_to_async(lambda:Player.objects.bulk_update(players, ['score']))()
        return True
    
    async def reset_players_guess_status(self) -> bool:
        players = await self.get_players_in_order()
        if not players:
            logging.error("Could not find players in order to reset players guess status")
            return False
        
        for player in players:
            player.guessed = False
        
        await sync_to_async(lambda:Player.objects.bulk_update(players, ['guessed']))()
        
        return True       
    
