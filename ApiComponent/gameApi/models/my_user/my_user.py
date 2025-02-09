from uuid import uuid4
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, \
    PermissionsMixin


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
    
    def create_superuser(self, email, username,password=None):
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


class MyUser(AbstractBaseUser, PermissionsMixin):

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
    creation_date = models.DateTimeField(auto_now_add=True)
    lastLogin = models.DateTimeField(auto_now=True)
    hide_contact_data = models.BooleanField(default=True)

    bio = models.TextField(max_length=500, default="", blank=True)
    in_game = models.BooleanField(default=False)
    games_played = models.PositiveSmallIntegerField(null=False, default=0)
    games_won = models.PositiveSmallIntegerField(null=False, default=0)

    # image = models.ImageField(
    #     null=True,
    #     blank=True,
    #     upload_to=lambda obj, filename: f'images/{obj.username}/{filename}',
    #     default='images/model.png'
    # )

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
        self.save()

    def clear_in_game(self):
        self.in_game = False
        self.save()

    def inc_games_played(self):
        self.games_played += 1
        self.save()

    def inc_games_won(self):
        self.games_won += 1
        self.save()

    def dec_games_played(self):
        self.games_played -= 1
        self.save()

    def dec_games_won(self):
        self.games_won -= 1
        self.save()
