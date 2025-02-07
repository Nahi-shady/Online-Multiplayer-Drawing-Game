# urls.py

from django.urls import path
from .views import RoomView, GetCsrfTokenView

urlpatterns = [
    path('get-csrf-token', GetCsrfTokenView.as_view(), name='get-csrf-token'),
    path('rooms', RoomView.as_view(), name='rooms'),
]
