import json
from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self): # Called when a WebSocket connection is opened
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    async def receive(self, text_data):
        json_text = json.load(text_data)
        message = json_text['message']
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'text-message',
                'message': message,
            }
        )
        
    async def chat_message(self, event):
        message = event['message']
        
        await self.send(
            text_data=json.dumps(
                {'message': message}
                )
            )