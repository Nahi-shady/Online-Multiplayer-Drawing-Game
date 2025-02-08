from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('games.urls')),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]

