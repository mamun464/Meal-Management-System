from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializer import UserRegistrationSerializer ,UserLoginSerializer,UserProfileSerializer,UserChangePasswordSerializer,SendPasswordResetEmailSerializer,UserPasswordRestSerializer,UserProfileEditSerializer, ChangeManagerSerializer,AllUserListSerializer
from django.contrib.auth import authenticate,login
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from account.models import CustomUser
from rest_framework.renderers import JSONRenderer
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import ProtectedError
from django.contrib.auth import logout
import requests


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    def post(self,request,format=None):
        # IsAuthenticated applied
        self.permission_classes = [IsAdminUser]

        self.check_permissions(request)

        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token=get_tokens_for_user(user)
            return Response({
                'msg':'New Registration Successful',
                'new_user': serializer.data,
                 'token':token ,
                },status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# Create your views here.

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        
        serializer = UserLoginSerializer(data=request.data)         
        if serializer.is_valid(raise_exception=True):
            # Access both the authenticated user and validated data from the serializer
            validated_data = serializer.validated_data
            user = validated_data['user']

            # Your existing logic here
            user.last_login = timezone.now()
            user.save()
            # Log the user in (if needed)
            login(request, user)
            token=get_tokens_for_user(user)
            return Response({
                'msg': 'Login successful',
                'token':token,
                },status=status.HTTP_200_OK)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        
        try:
            refresh_token = request.data.get('refresh_token')

            if not refresh_token:
                return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

            
            logout(request)
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'msg': 'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': f'An error occurred during logout: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
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
    
#for deleted user

class UserDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    renderer_classes = [UserRenderer]

    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({'errors': f"{id} isn't Found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is a staff or superuser
        if user.is_superuser:
            return Response({'msg': 'Deletion of same or upper post accounts is not allowed.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user.delete()
        except ProtectedError as e:
            return Response({'msg': f'User {user.fullName} cannot be deleted because they have data in other DB.'}, status=status.HTTP_403_FORBIDDEN)

        return Response({'msg': f'{user.fullName} deleted from your system'}, status=status.HTTP_204_NO_CONTENT)
    
class UserStatusChangeView(APIView):
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]
    renderer_classes = [UserRenderer]

    def put(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({'errors': f"{id} isn't Found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is already deactivated
        # if not user.is_active:
        #     return Response({'msg': f'User {user.fullName} is already deactivated'}, status=status.HTTP_200_OK)

        # Deactivate the user
        user.is_active = not user.is_active
        user.save()

        return Response({'msg': f'User {user.fullName} status-change in database'}, status=status.HTTP_200_OK)

class UserEditView(APIView):

    # IsAuthenticated applited
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    # def get(self, request, format=None):
    #     serializer = UserProfileSerializer(request.user)
        
    #     return Response(serializer.data,status= status.HTTP_200_OK)

    def put(self,request):
        serializer = UserProfileEditSerializer(request.user)
        userData=serializer.data
        user_id = userData['id']
        try:
            user=CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
             return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer=UserProfileEditSerializer(user,data=request.data,  partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ChangeManagerView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAdminUser]

    def put(self, request):
        newManager_id = request.query_params.get('newManager_id', None)

        if newManager_id is None:
            return Response({'error': 'Next Manager ID is required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)

        if not newManager_id.isdigit():
            return Response({'error': "'newManager_id' expected a number but got other"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            nextManager = CustomUser.objects.get(id=newManager_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Next manager not found.'}, status=404)
        
        try:
            currentManager = CustomUser.objects.get(id=request.user.id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Current manager not found.'}, status=404)


        # Change Manager ship
        if currentManager.id != nextManager.id:
            # Update is_staff attribute using the serializer

            if currentManager.is_superuser:
                searchManager = CustomUser.objects.filter(is_staff=True, is_manager=True).first()

                if searchManager is not None:
                        nextManager_serializer = ChangeManagerSerializer(nextManager, {'is_staff': True, 'is_manager': True}, partial=True)
                        nextManager_serializer.is_valid(raise_exception=True)
                        nextManager_serializer.save()

                        currentManager_serializer = ChangeManagerSerializer(searchManager, {'is_staff': False, 'is_manager': False}, partial=True)
                        currentManager_serializer.is_valid(raise_exception=True)
                        currentManager_serializer.save()
                        return Response({'msg': 'Manager changed successfully'}, status=status.HTTP_200_OK)
                else:
                    nextManager_serializer = ChangeManagerSerializer(nextManager, {'is_staff': True, 'is_manager': True}, partial=True)
                    nextManager_serializer.is_valid(raise_exception=True)
                    nextManager_serializer.save()
                    return Response({'msg': 'Manager changed successfully'}, status=status.HTTP_200_OK)
                
            
            nextManager_serializer = ChangeManagerSerializer(nextManager, {'is_staff': True, 'is_manager': True}, partial=True)
            nextManager_serializer.is_valid(raise_exception=True)
            nextManager_serializer.save()

            currentManager_serializer = ChangeManagerSerializer(currentManager, {'is_staff': False, 'is_manager': False}, partial=True)
            currentManager_serializer.is_valid(raise_exception=True)
            currentManager_serializer.save()
            return Response({'msg': 'Manager changed successfully'}, status=status.HTTP_200_OK)
        
        # else:
        #     return Response({'msg' :'You are already manager'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class AllUserListView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request):
        # Retrieve all active users
        active_users = CustomUser.objects.filter(is_superuser=False)

        # Serialize the active users
        serializer = AllUserListSerializer(active_users, many=True)

        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)
class ActiveUserListView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request):
        # Retrieve all active users
        active_users = CustomUser.objects.filter(is_active=True , is_superuser=False)

        # Serialize the active users
        serializer = AllUserListSerializer(active_users, many=True)

        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)
class DeactiveUserListView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request):
        # Retrieve all active users
        active_users = CustomUser.objects.filter(is_active=False , is_superuser=False)

        # Serialize the active users
        serializer = AllUserListSerializer(active_users, many=True)

        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)


class PhotoUpload(APIView):
    
    def upload_to_imagebb(self, api_key, image_data):
        api_url = "https://api.imgbb.com/1/upload"
        files = {"image": image_data}
        params = {"key": api_key}

        response = requests.post(api_url, files=files, params=params)

        try:
            result = response.json()

            # Check if the upload was successful
            if result['success']:
                return result["data"]["url"]

            # If not successful, handle the error
            error_msg = result.get("error", "Unknown error")
            print("Error in JSON response:", error_msg)
        except ValueError:
            # If the content is not in JSON format, print the raw content
            print("Non-JSON response content:", response.content)

        return None

    def put(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({'error': f"User with ID {id} not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if 'user_profile_img' key is present in the request data
        if 'user_profile_img' in request.data:
            # Assuming you have an image file in the request data
            image_file = request.data.get("user_profile_img")

            # Handle the case where image_file is None
            if image_file is None:
                # If no image is provided, store None in the user_profile_img field
                user.user_profile_img = None
            else:
                # Replace 'your_api_key' with your actual ImageBB API key
                api_key = "db34544520f57ff0f15d2b1ece2794b3"
                print("Image received")

                # Upload the image to ImageBB
                image_url = self.upload_to_imagebb(api_key, image_file.read())
                print("Image Url", image_url)

                if image_url:
                    # Update the user's profile image URL in the database
                    user.user_profile_img = image_url
                else:
                    return Response({'error': 'Failed to upload image'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save the user object after processing the image (or lack thereof)
        user.save()

        return Response({'msg': f'Profile image for {user.username} updated successfully'}, status=status.HTTP_200_OK)


                


