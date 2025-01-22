import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'illustra_backend.settings')

from django.core.asgi import get_asgi_application
from django.core.asgi import get_asgi_application
from django.apps import apps

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from games.models import Player, Room
from games import routing

async def lifespan(scope, receive, send):
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                print("ASGI server starting up...")
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                print("ASGI server shutting down...")
                # Perform cleanup tasks
                await clear_player_and_room_data()
                await send({'type': 'lifespan.shutdown.complete'})
                break

async def clear_player_and_room_data():
    try:
        Room = await apps.get_model('games', 'Room')
        await Room.objects.all().delete()
        print("Clearing Player and Room data...")
    except Exception as e:
        print(f"Error clearing Player and Room data: {e}")





application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns  # Define WebSocket URLs here
        )
    ),
    "lifespan": lifespan,
})
