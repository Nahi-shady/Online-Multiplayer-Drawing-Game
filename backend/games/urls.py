# urls.py

from django.urls import path
from .views import CreateRoomView, JoinRoomView, LeaveRoomView

urlpatterns = [
    path('create-room', CreateRoomView.as_view(), name='create-room'),
    path('join-room', JoinRoomView.as_view(), name='join-room'),
    path('leave-room', LeaveRoomView.as_view(), name='leave-room'),
]
