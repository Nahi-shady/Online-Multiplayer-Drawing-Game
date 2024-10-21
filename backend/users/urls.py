from rest_framework_simplejwt.views import TokenObtainPairView

from django.urls import path
from .jwt_serializers import EmailTokenObtainPairSerializer
from .views import UserCreateView, UserDetailView

urlpatterns = [
    path('<int:pk>', UserDetailView.as_view(), name='user-detail'),
    path('register', UserCreateView.as_view(), name='register'),
    path('login', TokenObtainPairView.as_view(serializer_class=EmailTokenObtainPairSerializer), name='token_obtain_pair'),
]