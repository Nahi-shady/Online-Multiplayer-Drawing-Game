import json
from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer

from django.db.models import F

from .models import Room, Player

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.score_set = 450
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
            {
                'type': 'player_joined',
            }
        )
        
        players = await self.get_players_by_order()
        await self.send(json.dumps({
            "type": "player_list",
            "players": [player.to_dict() for player in players],
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        await self.channel_layer.groud_send(
            self.room_group_name,
            {
                'type': 'player_left'
            }
        )
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'guess':
            await self.handle_guess(data.get('guess'))
            
        
    # game logic
    async def handle_guess(self, guess):
           room = await self.get_room()
           
           if room and guess.lower() == room.current_word.lower():
                await self.update_scores(self.player_id)
                player = await self.get_player()
                await self.send(
                    json.dumps(
                        {
                            'type': 'correct_guess',
                            'player_id': player.id,
                            'player_name': player.name
                        }
                    )
                )
       
    async def update_scores(self, player_id):
        player = await sync_to_async(Player.objects.get)(id=player_id)
        player.score = F['score'] + self.score_set
        await sync_to_async(player.save)()
        
        room = await self.get_room()
        drawer = room.current_drawer
        drawer.score = F['score'] + 30
        await sync_to_async(drawer.save)()
        
        self.score_set -= 33
        
        await self.update_leaderboard()
        
    async def update_leaderboard(self):
        players = await self.get_players_in_order()
        sorted_players = sorted(players, key=lambda x: -x.score)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'leaderboard_update',
                'leaderboard': [player.to_dict() for player in sorted_players]
            }
        )
        
     
    # messenger
    async def player_joined(self, event):
        player = await self.get_player()
        
        await self.send(
            json.dumps(
            {
                'type': 'player joined',
                'player_id': player.id,
                'player_name': player.name,
            })
        )
    async def player_left(self, event):
        player = await self.get_player()
        
        await self.send(
            json.dumps(
            {
                'type': 'player left',
                'player_id': player.id,
                'player_name': player.name,
            })
        )
    async def leaderboard_update(self, event):
        await self.send(
            json.dumps(
                {
                    'type': 'leaderboard_update',
                    'leaderboard': event['leaderboard']
                }
            )
        )
        
    # helper
    @sync_to_async
    async def get_player(self):
        return Player.objects.get(id=self.player_id)
    @sync_to_async
    async def get_room(self):
        return Room.objects.get(id=self.room_id)
    
    @sync_to_async
    def get_players_in_order(self):
        room = await self.get_room()
        return list(Player.objects.filter(room=room).order_by("turn_order"))