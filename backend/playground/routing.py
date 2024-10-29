# routing.py
from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('ws/game/<str:room_name>/', consumers.GameConsumer.as_asgi()),
    re_path('ws/game/test/', consumers.TestConsumer.as_asgi()),
]
