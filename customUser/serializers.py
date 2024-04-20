from rest_framework import serializers
import bleach
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

from .models import MyUser

# 
# DTO classes
# 

class MyUserAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ['id', 'email', 'username', 'phone_number', 'creation_date',
                  'last_login', 'hide_contact_data', 'is_admin']

class MyUserAccountDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ['id','email', 'username', 'phone_number',
                  'creation_date', 'hide_contact_data']

class MyUserPublicGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id','username', 'email')   

class MyUserPublicDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id','username', 'email', 'creation_date', 'last_login')   

class MyUserCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'password', 'phone_number',
                  'hide_contact_data', 'bio')
        
    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
        return value

    def validate_username(self, value):
        value = bleach.clean(value)
        if len(value) < 6 or len(value) > 50:
            raise serializers.ValidationError(
                "Username length must be between 6 and 50.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def validate_phone_number(self, value):

        if value is None:
            return None
        
        number = 0
        try:
            number = int(value)
        except:
            raise serializers.ValidationError(
                "Phone number must be forwarded as 9 digits without"
                + " any other signs.")
        
        if number < 999999999 and number > 111111111:
            return number
        else:
            raise serializers.ValidationError("Ivalid value of phone number")
        
    def validate_bio(self, value):
        value = bleach.clean(value)
        if len(value) > 500:
             raise serializers.ValidationError("Provided bio is too long."
                                               +" You can use up to 500 signs.")
        return value
