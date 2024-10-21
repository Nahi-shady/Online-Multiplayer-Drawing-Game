from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404
from .serializers import UserModelSerializer
from .models import User

# Create your views here.

class UserCreateView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data, status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserDetailView(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, id=pk)
        
        serializer = UserModelSerializer(user)
        
        return Response(serializer.data, status=status.HTTP_200_OK)