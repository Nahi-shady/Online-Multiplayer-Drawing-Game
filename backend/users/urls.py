from rest_framework_simplejwt.views import TokenObtainPairView

from django.urls import path
from .jwt_serializers import EmailTokenObtainPairSerializer
from .views import UserCreateView

urlpatterns = [
    path('register', UserCreateView.as_view(), name='register'),
    path('login', TokenObtainPairView.as_view(serializer_class=EmailTokenObtainPairSerializer), name='token_obtain_pair'),
]