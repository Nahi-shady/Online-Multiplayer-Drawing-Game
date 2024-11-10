import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import F
from .models import Room, Player
import asyncio

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = int(self.scope['url_route']['kwargs']['player_id'])
        self.room_id = int(self.scope['url_route']['kwargs']['room_id'])
        self.room_group_name = f'room_{self.room_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'player_joined', 'id': self.player_id}
        )
        
        await self.update_leaderboard()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'player_left', 'id': self.player_id}
        )
        await self.update_leaderboard()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        room = await self.get_room()
        player = await self.get_player()
        
        if message_type == "guess":
            await self.handle_guess(room, player, data.get('guess'))
        elif message_type == "new_game":
            await self.new_game(room)
        else:
            await self.send(json.dumps({"error": "Unknown message type"}))

    async def handle_guess(self,room, player, guess):
        drawer = await sync_to_async(lambda: room.current_drawer)()
    
        correct = False    
        if room and player.id != drawer.id and guess.lower() == room.current_word.lower():
            await self.update_scores(room, player, drawer)
            correct = True
            
        await self.channel_layer.group_send(
            self.room_group_name,
                {
                'type': 'message',
                'name': player.name,
                'guess': guess,
                'correct': correct
                
            })

    async def update_scores(self, room, player, drawer):
        player.score = F('score') + room.score_pool
        await sync_to_async(player.save)()

        drawer.score = F('score') + (room.score_pool // room.current_players_count)
        await sync_to_async(drawer.save)()
        
        room.score_pool = F('score_pool') - 33
        await sync_to_async(room.save)()
        
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

    async def new_game(self, room):
        room.turn_count = 0
        await sync_to_async(room.save)()

        await self.start_next_turn()
        
    async def start_next_turn(self):
        room = await self.get_room()
        if room.turn_count >= 5:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": 'game_over'
                })
            return

        await self.set_next_drawer()
        drawer = await sync_to_async(lambda: room.current_drawer)()
        
        room.turn_count = F('turn_count') + 1
        room.score_pool = 450
        await sync_to_async(room.save)()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "new_turn",
                "drawer_name": drawer.id,
                "turn": room.turn_count,
                "word": '-'*len(room.current_word),
            })
        await self.start_turn_timer(room)

    async def start_turn_timer(self, room):
        for remaining in range(45, 0, -1):
            await asyncio.sleep(1)

            if remaining == 30:
                await self.provide_hint(-1)
            if remaining == 15:
                await self.provide_hint(1)

            # if remaining == 0:
            #     await self.start_next_turn()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "timeout",
            }
        )
        await self.start_next_turn()

    async def provide_hint(self, idx):
        room = await self.get_room()
        hint = ['-']*len(room.current_word)

        hint[-1] = room.current_word[-1]
        if idx == 1:
            hint[1] = room.current_word[1]
            
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "hint_update", "hint": ''.join(hint)}
        )

    # Player Events
    async def  message(self, event):
        await self.send(
            json.dumps({
                'type': 'message',
                'guess': event['guess'],
                'name': event['name'],
                'correct': event['correct']}
                
                ))

    async def player_joined(self, event):
        await self.send(json.dumps({'type': 'player_joined', 'id': event['id']}))

    async def player_left(self, event):
        await self.send(json.dumps({'type': 'player_left', 'id': event['id']}))

    async def leaderboard_update(self, event):
        await self.send(json.dumps({'type': 'leaderboard_update', 'leaderboard': event['leaderboard']}))

    async def hint_update(self, event):
        await self.send(json.dumps({'type': 'hint_update', 'hint': event['hint']}))

    async def new_turn(self, event):
        await self.send(json.dumps({'type': 'new_turn'}))
        
    async def timeout(self, event):
        room = await self.get_room()
        word = room.current_word
        await self.send(json.dumps({"type": "timeout", "word": word}))

    async def game_over(self, event):
        players = await self.get_scoreboard()
        await self.send(json.dumps({"type": "game_over", "score_board": [{"name": player.name, "score":player.score} for player in players]}))
        

    # Helper Methods
    async def get_player(self):
        return await sync_to_async(Player.objects.get)(id=self.player_id)

    async def get_room(self):
        return await sync_to_async(Room.objects.get)(id=self.room_id)

    async def get_players_in_order(self):
        return await sync_to_async(lambda: list(Player.objects.filter(room_id=self.room_id).order_by("turn_order")))()
    async def get_scoreboard(self):
        return await sync_to_async(lambda: list(Player.objects.filter(room_id=self.room_id).order_by("score")))()

    async def set_next_drawer(self):
        room = await self.get_room()
        await sync_to_async(room.set_next_drawer)()
