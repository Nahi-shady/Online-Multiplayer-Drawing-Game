# urls.py

from django.urls import path
from .views import CreateRoomView, JoinRoomView

urlpatterns = [
    path('create-room', CreateRoomView.as_view(), name='create-room'),
    path('join-room', JoinRoomView.as_view(), name='join-room'),
]
