from rest_framework import serializers
import bleach
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

from .models.my_user.my_user import MyUser
from .models.game_archive.game_archive import GameArchive

# 
# DTO classes
#


class MyUserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'email', 'username', 'phone_number', 'creation_date',
                  'last_login', 'hide_contact_data', 'is_admin', 'bio',
                  'games_played', 'games_won'
                ]

class MyUserGetAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'username', 'games_played', 'games_won')   

class MyUserGetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'email', 'username', 'creation_date', 'last_login',
                  'hide_contact_data', 'bio', 'games_played', 'games_won'
                ]

class MyUserGetDetailPrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'email', 'username', 'phone_number', 'creation_date',
                  'hide_contact_data', 'bio', 'games_played', 'games_won'
                ]   

class MyUserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('username', 'email', 'password', 'phone_number',
                  'hide_contact_data', 'bio')
        
    def validate_email(self, email):
        cleaned_email = bleach.clean(email)
        try:
            validate_email(cleaned_email)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
        
        if MyUser.objects.filter(email__iexact=cleaned_email).exists():
            raise serializers.ValidationError("This email is already used.")

        return cleaned_email

    def validate_username(self, username):
        cleaned_username = bleach.clean(username)
        username_len = len(cleaned_username)

        if username_len < 6 or username_len > 50:
            raise serializers.ValidationError(
                "Username length must be between 6 and 50.")
        
        if MyUser.objects.filter(username__iexact=cleaned_username).exists():
            raise serializers.ValidationError("This username is already used.")
        
        return cleaned_username

    def validate_password(self, password):
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return password
    
    def validate_phone_number(self, phone_number):
        if phone_number is None:
            return None
        
        number = 0
        try:
            number = int(phone_number)
        except:
            raise serializers.ValidationError(
                "Phone number must be forwarded as 9 digits without"
                + " any other signs.")
        
        if number < 999999999 and number > 100000000:
            return number
        else:
            raise serializers.ValidationError("Ivalid phone number")
        
    def validate_bio(self, bio):
        cleaned_bio = bleach.clean(bio)
        if len(cleaned_bio) > 500:
            raise serializers.ValidationError("Provided bio is too long."
                                               +" You can use up to 500 signs.")
        return cleaned_bio


class GameArchiveGetAllSerializer(serializers.ModelSerializer):
    teacher_player = MyUserGetAllSerializer(read_only=True)
    student_player = MyUserGetAllSerializer(read_only=True)

    class Meta:
        model = GameArchive
        fields = ['start_date', 'start_time', 'lenght_in_sec', 'winner',
                  'student_player', 'teacher_player'
                ]
