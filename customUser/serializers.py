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
                  'bio', 'hide_contact_data']

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
        len = len(cleaned_username)

        if len < 6 or len > 50:
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
