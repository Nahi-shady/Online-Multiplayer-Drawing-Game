from django.apps import AppConfig
from .shutdown import shutdown_handler
import signal

class GameAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'games'

    def ready(self):
        # Register shutdown signals
        signal.signal(signal.SIGINT, shutdown_handler)  # Handle Ctrl+C
        signal.signal(signal.SIGTERM, shutdown_handler)  # Handle stop command