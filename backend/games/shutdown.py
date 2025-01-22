import threading
import signal
import sys

from django.db import connections
from django.apps import apps

# Save the default SIGINT handler to restore later if needed
original_sigint_handler = signal.getsignal(signal.SIGINT)

def shutdown_handler(signal_received, frame):
    print("Server is shutting down...")

    try:
        Room = apps.get_model('games', 'Room')
        Room.objects.all().delete()
        print("Player and Room data cleared.")
    except Exception as e:
        print(f"Error clearing Player and Room data: {e}")
    finally:
        sys.exit(0)
    # Close database connections

    for connection in connections.all():
        connection.close()
    print("Database connections closed. Cleanup completed.")


# Restore default SIGINT behavior after handling
signal.signal(signal.SIGINT, shutdown_handler)