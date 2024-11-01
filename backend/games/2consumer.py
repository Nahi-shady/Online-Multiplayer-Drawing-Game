import json
from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer

from django.db.models import F

from .models import Room, Player

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = int(self.scope['url']['kwargs']['player_id'])
        self.room_code = int(self.scope['url']['kwargs']['room_code'])
        self.room_group_name = f'room_{self.room_code}'
        
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
        
    # helper
    @sync_to_async
    async def get_player(self):
        return Player.objects.get(id=self.player_id)
    
    @sync_to_async
    def get_players_in_order(self):
        return list(Player.objects.filter(room_id=self.room_id).order_by("turn_order"))