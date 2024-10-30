# urls.py
from django.urls import path
from .views import RoomView

urlpatterns = [
    path('room/create', RoomView.as_view(), name='room-create'),
]
