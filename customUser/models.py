from uuid import uuid4
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class MyUserCreator(BaseUserManager):

    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("User must have an email adress.")
        if not username:
            raise ValueError("User must have an username.")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username,password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin): 

    # def user_directory_path(instance, filename):
    #     return 'avatars/user_{0}/{1}'.format(instance.username, filename)
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(
        max_length=50, unique=True, null=False, blank=False)
    phone_number = models.PositiveIntegerField(
        null=True, unique=True, blank=True)
    username = models.CharField(
        max_length=30, unique=True, null=False, blank=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    lastLogin = models.DateTimeField(auto_now=True)

    bio = models.TextField(max_length=500, default="")
    in_game = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)

    hide_contact_data = models.BooleanField(default=True)
    # image = models.ImageField(
    # null=True, blank=True, upload_to=user_directory_path, default="model.png")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_admin=models.BooleanField(default=False)

    objects = MyUserCreator()

    def __str__(self):
        return self.username

    def set_in_game(self):
        self.in_game = True

    def unset_in_game(self):
        self.in_game = False
