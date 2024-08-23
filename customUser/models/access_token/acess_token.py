from django.conf import settings
from django.db import models

from ..my_user.my_user import MyUser


class AccessToken(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
