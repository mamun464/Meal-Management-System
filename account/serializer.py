from rest_framework import serializers
from account.models import CustomUser
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class UserRegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'fullName', 'phone_no','password', 'password2',]
        extra_kwargs = {
            'password':{'write_only':True}
        }

    #validate password and confirm password is same
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

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
        PassResetLink = 'https://localhost:3000/api/user/reset'+EncodedUserId+'/'+token
        print('PassResetLink:',PassResetLink)

        #Email Send Code
        
        return attrs


     else:
        raise ValidationError("Email not registered in central Database!")

    


