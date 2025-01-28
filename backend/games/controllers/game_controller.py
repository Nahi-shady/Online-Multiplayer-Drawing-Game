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
        
        await self.update_leaderboard()
        
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
        
        await self.update_leaderboard()
        
        return True

    async def handle_message(self, player_id: int, data: dict) -> bool:
        message_type = data.get('type')
        
        if message_type == 'drawing':
            await sync_to_async(channel_layer.group_send)(
                self.room_group_name,{
                    'type': 'drawing',
                    'data': data })
        elif message_type == 'clear_canvas':
                await sync_to_async(channel_layer.group_send)(
                    self.room_group_name,{
                        'type': 'clear_canvas'})
        else:
            if message_type == 'guess':
                await self.handle_guess(player_id, data.get('guess'))
        
    async def handle_guess(self, player_id: int, guess: str) -> bool:
        correct = False
        player = await self.player_controller.get_player(player_id)
        
        if self.room_controller.update_scores(player_id, guess):
            correct = True
            if self.room_controller.guess_count >= self.room_controller.current_players_count - 1:
                if self.room_id in room_task:
                    room_task[self.room_id].cancel()
                    del room_task[self.room_id]
                    
                    await sync_to_async(channel_layer.group_send)(
                        self.room_group_name,
                        {"type": "message",
                        "message": "All guessed"})
                else:
                    await sync_to_async(channel_layer.group_send)(
                        self.room_group_name,
                        {"type": "message",
                        "message": "all guess not handled"})
                    await self.start_next_turn()
            await self.update_leaderboard()
            
        await sync_to_async(channel_layer.group_send)(
            self.room_group_name, {
                'type': 'guess',
                'name': player.name,
                'guess': guess,
                'correct': correct})
        
    async def update_leaderboard(self) -> bool:
        players = await self.player_controller.get_players_in_order()
        
        sorted_players = await sync_to_async(lambda: sorted(players, key=lambda x: -x.score))()
        players_list = await sync_to_async(lambda: [player.to_dict() for player in sorted_players])()
        
        await sync_to_async(channel_layer.group_send)(
            self.room_group_name,{
                'type': 'leaderboard_update',
                'leaderboard': players_list
            })