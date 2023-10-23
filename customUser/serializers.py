from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

import bleach

from .models import MyUser


class MyUserFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ['email', 'username', 'phone_number', 'creation_date', 'last_login', 'hide_contact_data']


class MyUserAccountDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ['email', 'username', 'last_login', 'creation_date', 'hide_contact_data']


class MyUserContactDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('username', 'email', 'phone_number')

class MyUserLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('username', 'email', 'last_login')   


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'password', 'phone_number')

    def validate_username(self, value):
        if len(value) < 6 or len(value) > 50:
            raise serializers.ValidationError("Username must be at least 6 characters long.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def validate_phone_number(self, value):

        if value is not None:
            number = 0
            try:
                number = int(value)
            except:
                raise serializers.ValidationError("Phone number must be forwarded as 9 digits without any other signs.")
            
            if number < 999999999 and number > 111111111:
                return number
            else:
                raise serializers.ValidationError("Phone number must be forwarded as 9 digits without any other signs.")
            
        return None


    def create(self, validated_data):
        user = MyUser.objects.create_user(
            bleach.clean(validated_data['email']),
            bleach.clean(validated_data['username']),
            validated_data['password']
        )

        if validated_data['phoneNumber'] is not None:
            user.phone_number = validated_data['phoneNumber']

        return user


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ('email', 'password')