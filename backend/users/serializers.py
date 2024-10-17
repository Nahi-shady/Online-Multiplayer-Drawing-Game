from datetime import datetime
from .models import User

from rest_framework.validators import UniqueValidator
from rest_framework import serializers

class UserModelSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    date_joined = serializers.CharField(read_only=True)
    
    queryset = User.objects.all()
    username = serializers.CharField(
        validators=[UniqueValidator(queryset)]
    )
    email = serializers.CharField(
        validators=[UniqueValidator(queryset)]
    )
    
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    nickname = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'nickname', 'email', 'password', 'confirm_password', 'date_joined']
        
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("password and confirm_password doesn't match")
        return data
    
    def create(self, data):
        data.pop('confirm_password')
        
        user = User(**data)
        user.set_password(data['password'])
        user.date_joined = datetime.now()
        user.save()
        
        return user