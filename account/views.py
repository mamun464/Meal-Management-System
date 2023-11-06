from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializer import UserRegistrationSerializer ,UserLoginSerializer,UserProfileSerializer,UserChangePasswordSerializer,SendPasswordResetEmailSerializer,UserPasswordRestSerializer
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token=get_tokens_for_user(user)
            return Response({'token':token ,'msg':'New Registration Successfull'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# Create your views here.

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            phone_no= serializer.data.get('phone_no')
            password= serializer.data.get('password')
            user = authenticate(phone_no=phone_no,password=password)

            if user is not None:
                token=get_tokens_for_user(user)
                return Response({'token':token, 'msg': 'Login successful'},status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non_field_errors':['Login Failed! Invalid Phone Number or Password']}},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        
        return Response(serializer.data,status= status.HTTP_200_OK)
    

class UserPasswordChangeView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer=UserChangePasswordSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Password Change successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Password Reset Link Send Your Register Email.Please Check.'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request,uid,token, format=None):
        serializer = UserPasswordRestSerializer(data=request.data,context={'uid':uid, 'token':token})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Password Reset successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                


