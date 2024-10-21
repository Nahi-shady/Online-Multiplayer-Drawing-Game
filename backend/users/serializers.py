import re
from datetime import datetime

from .models import User

from rest_framework.validators import UniqueValidator
from rest_framework import serializers


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if re.match(email_regex, email):
        return True
    else:
        return False

class UserModelSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    date_joined = serializers.CharField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    
    queryset = User.objects.all()
    username = serializers.CharField(
        validators=[UniqueValidator(queryset)]
    )
    email = serializers.CharField(
        validators=[UniqueValidator(queryset)]
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password', 'date_joined']
        
    def validate_email(self, value):
        if not is_valid_email(value):
            raise serializers.ValidationError("Invalid email format.")
        return value
    
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
        
        user = User.objects.create_user(email=data['email'], password=data['password'], **data)
        
        
        return user
    