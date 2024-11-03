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
            {'type': 'player_joined'}
        )
        
        await self.update_leaderboard()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'player_left'}
        )
        await self.update_leaderboard()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == "guess":
            await self.handle_guess(data.get('guess'))
        elif message_type == "next_turn":
            await self.start_next_turn()
        else:
            await self.send(json.dumps({"error": "Unknown message type"}))

    async def handle_guess(self, guess):
        room = await self.get_room()
        player = await self.get_player()
        guess_type = 'wrong_guess'
        
        if room and guess.lower() == room.current_word.lower():
            await self.update_scores()
            guess_type = 'correct_guess'
            
        await self.send(
            json.dumps({
                'type': guess_type,
                'player_id': player.id,
                'player_name': player.name,
                'guess': guess,
            })
        )

    async def update_scores(self):
        room = await self.get_room()
        player = await self.get_player()
        
        player.score = F('score') + room.score_pool
        await sync_to_async(player.save)()
        
        drawer = room.current_drawer
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

    async def start_next_turn(self):
        await self.set_next_drawer()
        room = await self.get_room()
        
        room.score_pool = 450
        await sync_to_async(room.save)()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "new_turn",
                "drawer_name": room.current_drawer.name,
                "word_length": len(room.current_word),
            }
        )
        await self.start_turn_timer()

    async def start_turn_timer(self):
        for remaining in range(45, 0, -1):
            await asyncio.sleep(1)
            
            if remaining in {25, 10}:
                await self.provide_hint()
                
            if remaining == 0:
                await self.start_next_turn()

    async def provide_hint(self):
        room = await self.get_room()
        
        if room.hint_letters < 2:
            room.hint_letters += 1
            hint = room.current_word[:room.hint_letters]
            await sync_to_async(room.save)()
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "hint_update", "hint": hint}
            )

    # Player Events
    async def player_joined(self, event):
        await self.send(json.dumps({'type': 'player_joined', 'id': self.player_id}))

    async def player_left(self, event):
        await self.send(json.dumps({'type': 'player_left', 'id': self.player_id}))

    async def leaderboard_update(self, event):
        await self.send(json.dumps({'type': 'leaderboard_update', 'leaderboard': event['leaderboard']}))

    async def hint_update(self, event):
        await self.send(json.dumps({'type': 'hint_update', 'hint': event['hint']}))

    async def new_turn(self, event):
        await self.send(json.dumps({"type": "new_turn", "drawer_name": event["drawer_name"]}))

    # Helper Methods
    async def get_player(self):
        return await sync_to_async(Player.objects.get)(id=self.player_id)

    async def get_room(self):
        return await sync_to_async(Room.objects.get)(id=self.room_id)

    async def get_players_in_order(self):
        return await sync_to_async(lambda: list(Player.objects.filter(room_id=self.room_id).order_by("turn_order")))()

    async def set_next_drawer(self):
        room = await self.get_room()
        await sync_to_async(room.set_next_drawer)()
