from rest_framework import serializers
from account.models import CustomUser
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from account.utils import Util
from django import forms

class UserRegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'fullName', 'phone_no','is_staff','password', 'password2',]
        extra_kwargs = {
            'password':{'write_only':True}
        }

    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        email = (attrs.get('email')).lower()
        print('Email-From-Validation:', email)
        #validate password and confirm password is same
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(f"{email} with this email already exists.")
        #validate password and confirm password is same
        if(password != password2):
            raise serializers.ValidationError("Confirm password not match with password!")

        return attrs
    
    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
    

class UserLoginSerializer(serializers.ModelSerializer):
        phone_no = serializers.CharField(max_length=20)
        class Meta:
            model = CustomUser
            fields = ['phone_no', 'password',]

class UserProfileSerializer(serializers.ModelSerializer):
     class Meta:
          model = CustomUser
          fields='__all__'


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
     
    class Meta:
            fields = ['password', 'password2']
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        user = self.context.get('user')

        if(password != password2):
            raise serializers.ValidationError("Confirm password not match with password!")
        

        user.set_password(password)
        user.save()
        return attrs
    

class SendPasswordResetEmailSerializer(serializers.Serializer): 
    email = serializers.EmailField(max_length=254)

    class Meta:
            fields = ['email']

    def validate(self, attrs):
     email = attrs.get('email')
     if CustomUser.objects.filter(email=email).exists():
        user= CustomUser.objects.get(email=email)
        EncodedUserId = urlsafe_base64_encode(force_bytes(user.id))
        print(EncodedUserId)
        token = PasswordResetTokenGenerator().make_token(user)
        print('Password ResetToken:',token)
        PassResetLink = 'http://127.0.0.1:8000/api/user/rest-password/'+EncodedUserId+'/'+token+'/'
        print('PassResetLink:',PassResetLink)

        #Email Send Code
        bodyContent = 'Click here to RESET YOUR PASSWORD: '+PassResetLink
        data={
             'subject': 'Reset Your Password',
             'body': bodyContent,
             'to_email': user.email

        }
        Util.send_email(data)
        
        return attrs
     else:
        raise ValidationError("Email not registered in central Database!")
     

class UserPasswordRestSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
     
    class Meta:
            fields = ['password', 'password2']
    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')

            encodedID = self.context.get('uid')
            token = self.context.get('token')

            if(password != password2):
                raise serializers.ValidationError("Confirm password not match with password!")
            

            decodeID = smart_str(urlsafe_base64_decode(encodedID))

            print("Decoded Id: ",decodeID)
            
            user= CustomUser.objects.get(id=decodeID)
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise ValidationError("Token is not Valid or Expired")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user,token)
            raise ValidationError("Token is not Valid or Expired")
        

class UserProfileEditSerializer(serializers.ModelSerializer):
     class Meta:
          model = CustomUser
          exclude = ['is_staff', 'is_active', 'is_superuser']
          
    


