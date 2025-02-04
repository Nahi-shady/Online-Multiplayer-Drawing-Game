import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'illustra_backend.settings')

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from games import routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns  # Define WebSocket URLs here
        )
    )
})
