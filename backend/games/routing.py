# routing.py
from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('ws/game/<str:room_code>', consumers.GameConsumer.as_asgi()),
]
