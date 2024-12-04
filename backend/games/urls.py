# urls.py

from django.urls import path
from .views import CreateRoomView, JoinRoomView, GetCsrfTokenView

urlpatterns = [
    path('get-csrf-token/', GetCsrfTokenView.as_view(), name='get-csrf-token'),
    path('create-room', CreateRoomView.as_view(), name='create-room'),
    path('join-room', JoinRoomView.as_view(), name='join-room'),
]
