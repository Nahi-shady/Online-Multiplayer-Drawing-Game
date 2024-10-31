from django.contrib import admin
from django.urls import path, include
import games, users, chat
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', include('games.urls')),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]

