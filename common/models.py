import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from common.managers import UserManager


class TimestampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# Create your models here.
class User(AbstractUser, TimestampedModel):
    username = None  # disable the AbstractUser.username field
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
