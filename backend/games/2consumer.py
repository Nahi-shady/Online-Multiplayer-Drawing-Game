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
        
        
    