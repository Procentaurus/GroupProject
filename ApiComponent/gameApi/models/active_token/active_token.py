from django.conf import settings
from django.db import models

from ..my_user.my_user import MyUser


class ActiveToken(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.created_at}'
