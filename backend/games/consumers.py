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

room_task = {}

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = int(self.scope['url_route']['kwargs']['player_id'])
        self.room_id = int(self.scope['url_route']['kwargs']['room_id'])
        
        self.room_group_name = f'room_{self.room_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name)
        
        await self.accept()
        
        await self.send(json.dumps({"type": "ping"}))
        print('ping')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'player_joined', 'id': self.player_id})
        
        await self.update_leaderboard()

    async def disconnect(self, close_code):
        player = await self.get_player()
        room = await self.get_room()
        if not player or not room:
            raise DenyConnection("player or room doens't exist")
            return
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name)
        
        drawer = await sync_to_async(lambda: room.current_drawer)()
        if player == drawer:
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "skip_turn",
                 "message": "Drawer disconnected!"})
            
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
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'player_left', 'id': self.player_id})
            
        await self.remove_player()
        await sync_to_async(room.refresh_from_db)()
                
        if room.current_players_count < 1:
            if self.room_id in room_task:
                room_task[self.room_id].cancel()
                del room_task[self.room_id]
            
            await self.delete_room(room)
            return
        
        await self.update_leaderboard()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'drawing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'drawing',
                    'data': data})
        elif message_type == 'clear_canvas':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {'type': 'clear_canvas'})
        else:
            room = await self.get_room()
            player = await self.get_player()
            if not player or not room:
                raise DenyConnection("player or room doens't exist")
                return
        
            if message_type == "guess":
                drawer = await sync_to_async(lambda: room.current_drawer)()
                await self.handle_guess(room, player, drawer, data.get('guess'))
            elif message_type == "new_game":
                if room.current_players_count > 1 and not room.on:
                    await self.start_new_game(room)
            elif message_type == 'word_chosen':
                room.current_word = data['word']
                await sync_to_async(room.save)()
                
                await self.channel_layer.group_send(
                        self.room_group_name,
                        {"type": "hint_update", 
                            "hint": ''.join('-' if c != ' ' else ' ' for c in room.current_word)})
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "clear_modal"})
            else:
                await self.send(json.dumps({"error": "Unknown message type"}))

    async def handle_guess(self,room, player, drawer, guess):
        correct = False    
        if room.on and player.id != drawer.id and not player.guessed and guess.lower() == room.current_word.lower():
            await self.update_scores(room, player, drawer)
            correct = True
            
        await self.channel_layer.group_send(
            self.room_group_name,
                {
                'type': 'guess',
                'name': player.name,
                'guess': guess,
                'correct': correct
                
            })

    async def update_scores(self, room, player, drawer):
        player.score = F('score') + room.score_pool
        player.guessed = True
        await sync_to_async(player.save)()

        drawer.score = F('score') + (room.score_pool // room.current_players_count)
        await sync_to_async(drawer.save)()
        
        room.score_pool = F('score_pool') - 33
        room.guess_count = F('guess_count') + 1
        await sync_to_async(room.save)()
        await sync_to_async(room.refresh_from_db)()
        
        if room.guess_count >= room.current_players_count - 1:
            if self.room_id in room_task:
                room_task[self.room_id].cancel()
                del room_task[self.room_id]
                
                await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "message",
                 "message": "All guessed"})
            else:
                await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "message",
                 "message": "all guess not handled"})
                await self.start_next_turn()
                
        await self.update_leaderboard()

    async def update_leaderboard(self):
        players = await self.get_players_in_order()
        
        sorted_players = await sync_to_async(lambda: sorted(players, key=lambda x: -x.score))()
        players_list = await sync_to_async(lambda: [player.to_dict() for player in sorted_players])()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'leaderboard_update',
                'leaderboard': players_list
            }
        )
    
    async def start_new_game(self, room): # reset room values (i.e turn_count and player scores) and start a new game
        if self.room_id in room_task:
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": 'message',
                'message': 'game has already started'}
            )
            return
        
        room.turn_count = 0
        room.on = True
        await sync_to_async(room.save)()
        await self.reset_player_scores()

        timeout = 10
        await self.send(json.dumps({"type": "new_game", "timeout": timeout}))
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": 'new_game',
             'timeout': timeout,
             'broadcaster_id': self.player_id})
        
        await asyncio.sleep(timeout)
        
        await self.start_next_turn()

    async def start_next_turn(self):
        room = await self.get_room()
        if not room:
            print("Room does not exist, skipping turn.")
            return  # Exit gracefully if the room doesn't exist

        # End game if final turn is played
        if room.turn_count >= 5:
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "game_over"}
            )
            room.on = False
            await sync_to_async(room.save)()

            # Clean up room tasks
            if self.room_id in room_task:
                room_task[self.room_id].cancel()
                del room_task[self.room_id]
            return

        # Update room state for the next turn
        await self.set_next_drawer(room)
        await self.reset_players_guess_status()

        room.turn_count = F('turn_count') + 1
        room.score_pool = 450
        room.guess_count = 0
        room.current_word = ''
        await sync_to_async(room.save)()
        await sync_to_async(room.refresh_from_db)()

        drawer = await sync_to_async(lambda: room.current_drawer)()
        print(f"Drawer: {drawer.name}")

        # Start the new turn
        turn_timer = 30
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "new_turn",
                "drawer": drawer.name if drawer else '',
                "turn": room.turn_count,
                'timeout': turn_timer   # turn timer
            }
        )

        # Get word choices
        word_choices = await self.get_words()
        
        timeout = 10
        # Notify drawer with word choices
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "word_choices",
                "choices": word_choices,
                "drawer": drawer.name,
                "timeout": timeout
            }
        )
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "drawer_choosing_word",
                "timeout": timeout
            }
        )

        # Clear canvas for the next turn
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "clear_canvas"}
        )
 
        # Create async task for turn timer
        room_task[self.room_id] = asyncio.create_task(self.start_turn_timer(turn_timer))

    async def start_turn_timer(self, turn_timer):
        try:
            room = await self.get_room()
            if not room:
                print("Room does not exist, stopping turn timer.")
                return  # Exit if the room doesn't exist

            for remaining in range(turn_timer, 0, -1):
                print(remaining, self.player_id)
                await asyncio.sleep(1)
                
                if remaining == 20:
                    await sync_to_async(room.refresh_from_db)()
                    if not room.current_word:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {"type": "skip_turn", "message": "Drawer did not choose a word, skipping turn"}
                        )
                        break  # Skip the turn if no word is chosen
                    
                    await self.channel_layer.group_send(self.room_group_name, {"type": "clear_modal"})

                if remaining == 10:
                    await self.provide_hint(-1, room.current_word)
                if remaining == 5:
                    await self.provide_hint(1, room.current_word)

        except asyncio.CancelledError:
            print("Turn timer was cancelled.")
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "message", "message": "Turn skipped due to cancellation!"}
            )
        
        await self.start_next_turn()

    async def provide_hint(self, idx, selected_word):
        
        hint = ['-']*len(selected_word)
        hint[-1] = selected_word[-1]
        if idx == 1:
            hint[1] = selected_word[1]
            
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "hint_update", "hint": ''.join(hint)}
        )


    # Player Events
    async def  message(self, event):
        await self.send(
            json.dumps({
                'type': 'message',
                'message': event['message']}
                ))
        
    async def  guess(self, event):
        await self.send(
            json.dumps({
                'type': 'guess',
                'guess': event['guess'],
                'name': event['name'],
                'correct': event['correct']}
                ))

    async def player_joined(self, event):
        await self.send(json.dumps({'type': 'player_joined', 'id': event['id']}))

    async def player_left(self, event):
        await self.send(json.dumps({'type': 'player_left', 'id': event['id']}))
    
    #Game Events 
    async def leaderboard_update(self, event):
        await self.send(json.dumps({'type': 'leaderboard_update', 'leaderboard': event['leaderboard']}))

    async def new_game(self, event):
        if event.get("broadcaster_id") == self.player_id:
            return  # Ignore the message if this instance is the broadcaster
        await self.send(json.dumps({"type": "new_game", "timeout": event["timeout"]}))
        
    async def new_turn(self, event):
        await self.send(
            json.dumps({"type": "new_turn", 
                        "turn": event['turn'],
                        "drawer": event["drawer"],
                        'timeout': event['timeout']}))
    
    async def timeout(self, event):
        room = await self.get_room()
        if not room:
            raise DenyConnection("room doens't exist")
        
        word = room.current_word
        await self.send(json.dumps({"type": "timeout", "word": word}))

    async def game_over(self, event):
        players = await self.get_scoreboard()
        await self.send(json.dumps({"type": "game_over", "score_board": [{"name": player.name, "score":player.score} for player in players]}))

    async def skip_turn(self, event):
        await self.send(json.dumps({"type": "skipping_turn", 'message': event['message']}))
        
    async def clear_modal(self, event):
        await self.send(json.dumps({"type": "clear_modal"}))

    # drawing events
    async def drawer_choosing_word(self, event):
        await self.send(json.dumps({'type': 'drawer_choosing_word', 'timeout': event['timeout']}))

    async def word_choices(self, event):
        await self.send(json.dumps({'type': 'word_choices', 'choices': event['choices'], "drawer": event['drawer'], 'timeout': event['timeout']}))
   
    async def drawing(self, event):
        data = event['data']
        start = data.get('start')
        end = data.get('end')
        color = data.get('color')
        thickness = data.get('thickness')
        
        await self.send(
            json.dumps({'type': 'drawing', 'start': start,
                        'end': end, 'color': color,
                        'thickness': thickness}))
        
    async def clear_canvas(self, event):
        await self.send(json.dumps({"type": "clear_canvas"}))

    async def hint_update(self, event):
        await self.send(json.dumps({'type': 'hint_update', 'hint': event['hint']}))


    # Helper Methods
    async def get_player(self):
        try:
            return await sync_to_async(Player.objects.get)(id=self.player_id)
        except:
            return None

    async def get_room(self):
        try:
            return await sync_to_async(Room.objects.get)(id=self.room_id)
        except:
            return None

    async def get_players_in_order(self):
        return await sync_to_async(lambda: list(Player.objects.filter(room_id=self.room_id).order_by("joined_at")))()

    async def get_scoreboard(self):
        return await sync_to_async(lambda: list(Player.objects.filter(room_id=self.room_id).order_by("score")))()

    async def reset_player_scores(self):
        players = await self.get_players_in_order()
        for player in players:
            player.score = 0

        await sync_to_async(lambda:Player.objects.bulk_update(players, ['score']))()

    async def reset_players_guess_status(self):
        players = await self.get_players_in_order()
        for player in players:
            player.guessed = False
            
        await sync_to_async(lambda:Player.objects.bulk_update(players, ['guessed']))()

    async def set_next_drawer(self, room):
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
            new_drawer = None
        
        room.current_drawer = new_drawer
        await sync_to_async(room.save)()
    
    async def remove_player(self):
        player, room = await self.get_player(), await self.get_room()
        room.current_players_count = F('current_players_count') - 1
        await sync_to_async(room.save)()
        
        await sync_to_async(player.delete)()

    async def delete_room(self, room):
        room.on = False
        room.active = False
        await sync_to_async(room.save)()

        await sync_to_async(room.delete)()
        return

    async def get_words(self):
        word_1 = random.choice(EASY_WORDS)
        word_2 = random.choice(HARD_WORDS)
        word_3 = random.choice(FUN)
        
        while word_3.lower() == word_2.lower():
            word_2 = random.choice(HARD_WORDS)
        
        return [word_1, word_2, word_3]