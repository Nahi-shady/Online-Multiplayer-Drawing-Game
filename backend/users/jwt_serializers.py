import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from django.contrib.auth import get_user_model

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if re.match(email_regex, email):
        return True
    else:
        return False

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get("password")
        
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
    
        if not is_valid_email(email):
            raise serializers.ValidationError("Invalid email format.")
        
        user = get_user_model().objects.filter(email=email).first()
        if user and user.check_password(password):
            return super().validate(attrs)
        
        raise serializers.ValidationError('Invalid email or password')