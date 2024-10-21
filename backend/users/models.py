from datetime import datetime

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.db import models

from .managers import UserManager
# Create your models here.

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=25)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.username