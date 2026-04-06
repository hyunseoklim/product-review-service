from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    사용자 모델
    """
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username