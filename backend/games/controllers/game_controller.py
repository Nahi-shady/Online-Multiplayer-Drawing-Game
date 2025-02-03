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
from .helper_functions import get_word_choices

channel_layer = get_channel_layer()

room_task = {}

class GameController():
    def __init__(self, room_id):
        self.room_id = room_id
        self.room_group_name = f'room_{self.room_id}'
        
        self.player_controller = PlayerController(self.room_id)
        self.room_controller = RoomController(self.room_id)
        
    async def player_joined(self, player_id: int) -> bool:
        if self.player_controller.player_joined(player_id):
            await channel_layer.group_send(
                self.room_group_name, {
                    'type': 'player_joined',
                    'id': player_id})
            
            self.room_controller.current_players_count += 1
            
            return True
        
        await self.update_leaderboard()
        
        return False
    
    async def player_left(self, player_id: int) -> bool:
        player = await self.player_controller.get_player(player_id)
        drawer = await self.room_controller.get_drawer()
        
        if player and player == drawer:
            await channel_layer.group_send(
                self.room_group_name, {
                    "type": "skip_turn",
                 "message": "Drawer disconnected!"
                })
            
            if self.room_id in room_task:
                await channel_layer.group_send(
                    self.room_group_name,
                    {"type": "message", "message": "Drawer disconnected"}
                )
                
                room_task[self.room_id].cancel()
                del room_task[self.room_id]
            else:
                await channel_layer.group_send(
                self.room_group_name,
                    {"type": "message",
                    "message": "not handled drawer leave!"}
                )
        
        if await self.player_controller.remove_player(player_id):
            self.room_controller.current_players_count -= 1
            await channel_layer.group_send(
                self.room_group_name,{
                    'type': 'player_left',
                    'id': player_id})
        
        if not await self.room_controller.is_active():
            if self.room_id in room_task:
                room_task[self.room_id].cancel()
                del room_task[self.room_id]
            
            if not await self.room_controller.remove_room():
                logging.info("Room was not removed")
        
        await self.update_leaderboard()
        
        return True

    async def handle_message(self, player_id: int, data: dict) -> bool:
        if not data:
            print('Invalid message received')
            return False
        
        message_type = data.get('type')
        
        if message_type == 'drawing':
            await channel_layer.group_send(
                self.room_group_name,{
                    'type': 'drawing',
                    'data': data })
        elif message_type == 'clear_canvas':
                await channel_layer.group_send(
                    self.room_group_name,{
                        'type': 'clear_canvas'})
        else:
            await self.update_leaderboard()
            if message_type == 'guess':
                await self.handle_guess(player_id, data.get('guess'))
            elif message_type == 'word_chosen':
                word = data.get('word')
                if not word:
                    print('empty word choice')
                    return False
                
                await self.room_controller.word_chosen(word)

                await channel_layer.group_send(
                    self.room_group_name,{
                        "type": "hint_update", 
                        "hint": ''.join('-' if c != ' ' else ' ' for c in self.room_controller.current_word)})

                await channel_layer.group_send(
                    self.room_group_name,{
                        "type": "clear_modal"})
            elif message_type == 'new_game':
                await channel_layer.group_send(
                    self.room_group_name,{
                        'type': 'clear_canvas'})
                
                await self.start_new_game(player_id)
            
    async def handle_guess(self, player_id: int, guess: str) -> bool:
        correct = False
        player = await self.player_controller.get_player(player_id)
        
        if await self.room_controller.correct_guess(player_id, guess):
            correct = True
            
            if self.room_controller.guess_count >= self.room_controller.current_players_count - 1:
                if self.room_id in room_task:
                    await channel_layer.group_send(
                        self.room_group_name,{
                            "type": "message",
                            "message": "All guessed"})
                    room_task[self.room_id].cancel()
                    del room_task[self.room_id]
                    
                else:
                    await channel_layer.group_send(
                        self.room_group_name,
                        {"type": "message",
                        "message": "all guess not handled"})
                    await self.start_next_turn()
                    
            await self.update_leaderboard()
            
        if correct:
            await channel_layer.group_send(
                self.room_group_name,{
                    "type": "guess",
                    "name": player.name,})
        else:
            await channel_layer.group_send(
                self.room_group_name, {
                    'type': 'chat_message',
                    'name': player.name,
                    'message': guess,})
        
    async def update_leaderboard(self) -> bool:
        players = await self.player_controller.get_players_in_order()
        
        sorted_players = await sync_to_async(lambda: sorted(players, key=lambda x: -x.score))()
        players_list = await sync_to_async(lambda: [player.to_dict() for player in sorted_players])()
        
        await channel_layer.group_send(
            self.room_group_name,{
                'type': 'leaderboard_update',
                'leaderboard': players_list
            })
    
    async def start_new_game(self, player_id) -> bool:
        if self.room_id in room_task:
            await channel_layer.group_send(
                self.room_group_name,{
                    "type": 'message',
                    'message': 'game has already started',})
        
            return  False
        
        if not await self.room_controller.prepare_room_for_new_round() or not await self.player_controller.reset_player_scores():
            return False
        
        timeout = 10
        await channel_layer.group_send(
            self.room_group_name,{
                "type": 'new_game',
                'timeout': timeout,
                'broadcaster_id': player_id})
        
        asyncio.create_task(self.sleep_then_start_turn(timeout))
    
    async def start_next_turn(self) -> None:
        print("Starting next turn")
        await self.room_controller.refresh_room_db()
        
        if not await self.room_controller.room_is_ready():
            print("Room is not ready")
            scoreboard = await self.player_controller.get_scoreboard()
            await channel_layer.group_send(
                self.room_group_name,{
                    "type": "game_over",
                    "scoreboard": scoreboard})
        
            # Clean up room tasks
            if self.room_id in room_task:
                room_task[self.room_id].cancel()
                del room_task[self.room_id]
            return
        
        # Update room state for the next turn
        if not await self.room_controller.set_next_drawer() or not await self.player_controller.reset_players_guess_status() or not await self.room_controller.reset_room_for_new_turn():
            print("Something went wrong while resetting room and player for new turn")
            return
        
        drawer_name, turn_count = self.room_controller.drawer.name, self.room_controller.turn_count
        turn_timer = 30  
        await channel_layer.group_send(
            self.room_group_name,{
                "type": "new_turn",
                "drawer": drawer_name,
                "turn": turn_count,
                'timeout': turn_timer})
        
        # Get word choices
        word_choices = await get_word_choices()
        
        timeout = 10
        # Notify drawer with word choices
        await channel_layer.group_send(
            self.room_group_name,{
                "type": "word_choices",
                "choices": word_choices,
                "drawer": drawer_name,
                "timeout": timeout})
        
        await channel_layer.group_send(
            self.room_group_name,{
                "type": "drawer_choosing_word",
                "timeout": timeout})
    
        # Clear canvas for the next turn
        await channel_layer.group_send(
            self.room_group_name,{
                "type": "clear_canvas"})
 
        # Create async task for turn timer
        room_task[self.room_id] = asyncio.create_task(self.start_turn_timer(turn_timer))
        
    async def start_turn_timer(self, turn_timer):
        try:
            if not self.room_controller.room:
                print('Room does not exist, skipping turn')
                return  # Exit if the room doesn't exist

            for remaining in range(turn_timer, 0, -1):
                print(remaining)
                await asyncio.sleep(1)
                
                if turn_timer - remaining == 10:
                    # await self.room_controller.refresh_room_db()
                    if not self.room_controller.current_word:
                        await channel_layer.group_send(
                            self.room_group_name,
                            {"type": "skip_turn", "message": "Drawer did not choose a word, skipping turn"}
                        )
                        break  # Skip the turn if no word is chosen
                    
                    await channel_layer.group_send(
                        self.room_group_name, {
                            "type": "clear_modal"})

                if remaining == 15:
                    await self.provide_hint(-1, self.room_controller.current_word)
                if remaining == 10:
                    await self.provide_hint(1, self.room_controller.current_word)
        except asyncio.CancelledError:
            print("Turn timer was cancelled.")
            await channel_layer.group_send(
                self.room_group_name,{
                    "type": "message",
                    "message": "Turn skipped due to cancellation!"})

        timeout = 5
        scoreboard = await self.player_controller.get_scoreboard()
        await channel_layer.group_send(
                self.room_group_name, {
                    "type": "display_score",
                    "timeout": timeout,
                    "scoreboard": scoreboard,})
        
        asyncio.create_task(self.sleep_then_start_turn(timeout))
        
    async def provide_hint(self, idx, selected_word):
        
        hint = ['-']*len(selected_word)
        hint[-1] = selected_word[-1]
        if idx == 1:
            hint[1] = selected_word[1]
            
        await channel_layer.group_send(
            self.room_group_name,{
                "type": "hint_update",
                "hint": ''.join(hint) })

    async def sleep_then_start_turn(self, timeout):
        await asyncio.sleep(timeout)
        await self.start_next_turn()
