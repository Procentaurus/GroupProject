from uuid import uuid4
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class MyUserCreator(BaseUserManager):

    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("User must have an email adress.")
        if not username:
            raise ValueError("User must have an username.")
        user = self.model(
            email=email.lower(),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email=email.lower(),
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(
        max_length=50,
        unique=True,
        null=False,
        blank=False
    )
    phone_number = models.PositiveIntegerField(
        null=True,
        unique=True,
        blank=True
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        null=False,
        blank=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_admin=models.BooleanField(default=False)

    objects = MyUserCreator()

    def __str__(self):
        return self.username
    
    def has_module_perms(self, perm):
        pass

    def has_perm(self, perm, obj=None):
        # Implement permission check logic
        return True

    def has_module_perms(self, app_label):
        # Implement app label permission logic
        return True
