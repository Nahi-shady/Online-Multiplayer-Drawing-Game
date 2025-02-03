import json
import random
import logging
from asgiref.sync import sync_to_async
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection

from .controllers.utils import get_game_controller

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = int(self.scope['url_route']['kwargs']['player_id'])
        self.room_id = int(self.scope['url_route']['kwargs']['room_id'])
        self.room_group_name = f'room_{self.room_id}'
        
        self.game_controller = await get_game_controller(self.room_id)
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name)
        
        await self.accept()
        await self.game_controller.update_leaderboard()
        
        await self.send(json.dumps({"type": "ping"}))
        print('ping')
        
        if not await self.game_controller.player_joined(self.player_id):
            DenyConnection('Player could not join room')

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name)
        
        await self.game_controller.player_left(self.player_id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        await self.game_controller.handle_message(self.player_id, data)


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
                'name': event['name'], }))
        
    async def  chat_message(self, event):
        await self.send(
            json.dumps({
                'type': 'chat_message',
                'message': event['message'],
                'name': event['name'], }))


    async def player_joined(self, event):
        await self.send(json.dumps({'type': 'player_joined', 'id': event['id']}))

    async def player_left(self, event):
        await self.send(json.dumps({'type': 'player_left', 'id': event['id']}))
    
    #Game Events 
    async def leaderboard_update(self, event):
        await self.send(json.dumps({'type': 'leaderboard_update', 'leaderboard': event['leaderboard']}))

    async def display_score(self, event):
        print(event['scoreboard'])
        await self.send(json.dumps({"type": "display_score", "timeout": event['timeout'], "word": event["word"], "scoreboard": event['scoreboard']}))
    
    async def new_game(self, event):
        await self.send(json.dumps({"type": "new_game", "timeout": event["timeout"]}))
    
    async def new_turn(self, event):
        await self.send(
            json.dumps({"type": "new_turn", 
                        "turn": event['turn'],
                        "drawer": event["drawer"],
                        'timeout': event['timeout']}))
    
    async def game_over(self, event):
        await self.send(json.dumps({"type": "game_over", "scoreboard": event['scoreboard']}))

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

