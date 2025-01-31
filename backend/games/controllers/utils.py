import random
from collections import defaultdict

from .game_controller import GameController

game_controllers = defaultdict()

async def get_game_controller(room_id: int):
    if room_id not in game_controllers:
        game_controllers[room_id] = GameController(room_id)
    return game_controllers[room_id]

