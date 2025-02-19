from django.urls import re_path
from .consumers import GameConsumer

websocket_urlpatterns = [
    re_path(r"ws/(?P<room_id>\w+)/(?P<player_id>\w+)/$", GameConsumer.as_asgi()),
]
