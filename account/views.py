from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializer import UserRegistrationSerializer ,UserLoginSerializer,UserProfileSerializer,UserChangePasswordSerializer,SendPasswordResetEmailSerializer,UserPasswordRestSerializer,UserProfileEditSerializer, ChangeManagerSerializer,AllUserListSerializer
from django.contrib.auth import authenticate,login
from rest_framework.exceptions import AuthenticationFailed,ValidationError
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsOperationPermission
from account.models import CustomUser
from rest_framework.renderers import JSONRenderer
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import ProtectedError
from django.contrib.auth import logout
from account.utils import Util
import requests
import random
import string


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOperationPermission]
    def post(self,request,format=None):
        # IsAuthenticated applied
        self.permission_classes = [IsAdminUser]

        self.check_permissions(request)

        required_fields = ['email', 'fullName','email', 'phone_no']
        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'{field} is missing or empty',
                }, status=status.HTTP_400_BAD_REQUEST)
            
        # Generate an 8-digit random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        # for development purposes it will be removed after deployment
        password = "123456"

        # Create a mutable copy of the request data
        data = request.data.copy()
        data['password'] = password
        data['password2'] = password

        serializer = UserRegistrationSerializer(data=data)

        if serializer.is_valid():
            user = serializer.save()
            token=get_tokens_for_user(user)
            user_serializer = UserProfileSerializer(user)
            user_data = user_serializer.data

            #Send the Mail OTP verification
            bodyContent = f"Here is your Password: {password} \nPlease don't share it with anyone and change it after login"
            data={
                'subject': 'MMS Credentials',
                'body': bodyContent,
                'to_email': user.email,

            }

            email_sent=Util.send_email(data)
            if email_sent:
                return Response({
                    'success': True,
                    'status': status.HTTP_200_OK,
                    'message': 'Registration successful and credentials sent to your email',
                    'token': token,
                    'new_user': user_data,
                    
                    },status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': True,
                    'status': status.HTTP_200_OK,
                    'message': 'Registration successful but mail not sent Please reset your credentials',
                    'new_user': user_data,
                    'token': token,
                    
                }, status=status.HTTP_200_OK)
        
        
        else:
            errors = serializer.errors
            error_messages = []
            for field, messages in errors.items():
                error_messages.append(f"{field}: {messages[0]}")  # Concatenate field name and error message
            msg ="\n".join(error_messages)
            msg = msg.replace("non_field_errors: ", "")
            return Response({
                "success": False,
                "status": 400,
                "message": msg  # Join error messages with newline character
            }, status=status.HTTP_400_BAD_REQUEST)

# Create your views here.

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):

        required_fields = [ 'phone_no','password']
        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'{field} is missing or empty',
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserLoginSerializer(data=request.data)    

        try:
            validated_data = serializer.validate(request.data)
            user = validated_data['user']

            user.last_login = timezone.now()
            user.save()
            login(request, user)
            token = get_tokens_for_user(user)

            user_serializer = UserProfileSerializer(user)
            user_data = user_serializer.data

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'Successfully logged in',
                'token': token,
                'user_data': user_data,
            }, status=status.HTTP_200_OK)

        except (AuthenticationFailed, ValidationError) as e:
            status_code = status.HTTP_401_UNAUTHORIZED if isinstance(e, AuthenticationFailed) else status.HTTP_400_BAD_REQUEST
            return Response({
                'success': False,
                'status': status_code,
                'message': str(e),  # Use the error message from the exception
            }, status=status_code)

        except Exception as e:
            error_messages = []
            for field, messages in e.detail.items():
                error_messages.append(f"{field}: {messages[0]}")
            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': "\n".join(error_messages),
            }, status=status.HTTP_400_BAD_REQUEST)

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

class BulkDeleteUsersView(APIView):
    """
    API endpoint to delete multiple users by their IDs with checks for manager roles.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    renderer_classes = [UserRenderer]

    def delete(self, request, *args, **kwargs):
        # Ensure the data is a list
        if not isinstance(request.data, list):
            return Response(
                {
                    "success": False,
                    "status": 400,
                    "message": "Invalid data format. A list of user IDs is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_ids = request.data


        deleted_users = []

        for user_id in user_ids:
            try:
                user = CustomUser.objects.get(id=user_id)

                # Prevent deletion of superusers
                if user.is_superuser:
                    continue

                # Prevent deletion of managers
                if user.is_manager:
                    continue

                # Proceed with deletion
                user.delete()
                deleted_users.append(user_id)
            except CustomUser.DoesNotExist:
                continue
            except ProtectedError:
                continue
            except Exception:
                continue

        return Response({
            'success': True,
            'status': status.HTTP_200_OK,
            'message': "User deletion process completed.",
            'deleted_ids': deleted_users
        }, status=status.HTTP_200_OK)

class UserDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    renderer_classes = [UserRenderer]
    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'status': status.HTTP_404_NOT_FOUND,
                'message': f"User with ID {id} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is a superuser
        if user.is_superuser:
            return Response({
                'success': False,
                'status': status.HTTP_403_FORBIDDEN,
                'message': 'Deletion of superuser accounts is not allowed.'
            }, status=status.HTTP_403_FORBIDDEN)
        elif user.is_manager:
            return Response({
                'success': False,
                'status': status.HTTP_403_FORBIDDEN,
                'message': 'Please change the manager first before deleting the user.'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            user_id = user.id
            # Convert the single ID to a string
            deleted_users = str(user_id)
            user.delete()
            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': f"User {user.fullName} deleted successfully.",
                 'deleted_ids': deleted_users
            }, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({
                'success': False,
                'status': status.HTTP_403_FORBIDDEN,
                'message': f"User {user.fullName} cannot be deleted because they are referenced in other database entries."
            }, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': "An unexpected error occurred while deleting the user.",
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def put(self, request, *args, **kwargs):
        user = request.user
        required_fields = ['request_user_id']
        for field in required_fields:
            if field not in request.query_params or not request.query_params[field]:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': f'{field} is missing or empty',
                }, status=status.HTTP_400_BAD_REQUEST)

        request_user_id = request.query_params.get('request_user_id')

        # Check if the user ID in the request matches the authenticated user's ID
        if str(user.id) != str(request_user_id):
            # If the user is not the same, check for admin or manager roles
            if user.role not in ['admin', 'manager']:
                return Response({
                    'success': False,
                    'status': status.HTTP_403_FORBIDDEN,
                    'message': "You do not have permission to update this user's information.",
                }, status=status.HTTP_403_FORBIDDEN)
            
        

        try:
            # Fetch the user object by the ID provided in the request
            user_to_update = CustomUser.objects.get(pk=request_user_id)
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'User not found',
            }, status=status.HTTP_404_NOT_FOUND)

         # Check if `is_active` is being updated
        new_is_active = request.data.get('is_active')
        if new_is_active is not None and user_to_update.is_active != new_is_active:
            # Check if the current user is trying to change their own `is_active` field
            if user.id == user_to_update.id and user.role == 'manager':
                return Response({
                    'success': False,
                    'status': status.HTTP_403_FORBIDDEN,
                    'message': 'Managers cannot change their own active status.',
                }, status=status.HTTP_403_FORBIDDEN)
        
            
            # Only allow admins or managers to change `is_active`
            if user.role not in ['admin', 'manager']:
                return Response({
                    'success': False,
                    'status': status.HTTP_403_FORBIDDEN,
                    'message': 'Only admins or managers can change the active status.',
                }, status=status.HTTP_403_FORBIDDEN)

        # Check if `role` is being updated
        if user_to_update.role in ['admin', 'manager']:
            if user_to_update.is_active != request.data.get('is_active'):
                return Response({
                    'success': False,
                    'status': status.HTTP_403_FORBIDDEN,
                    'message': 'You cannot change the Status of an Admin or Manager.',
                }, status=status.HTTP_403_FORBIDDEN)

        # Proceed with partial update (allow missing fields)
        serializer = UserProfileEditSerializer(user_to_update, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'User updated successfully',
                'data': serializer.data,
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Invalid data',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    # # IsAuthenticated applited
    # renderer_classes = [UserRenderer]
    # permission_classes = [IsAuthenticated]

    # def put(self,request):
    #     serializer = UserProfileEditSerializer(request.user)
    #     userData=serializer.data
    #     user_id = userData['id']
    #     try:
    #         user=CustomUser.objects.get(pk=user_id)
    #     except CustomUser.DoesNotExist:
    #          return Response(status=status.HTTP_404_NOT_FOUND)
        
    #     serializer=UserProfileEditSerializer(user,data=request.data,  partial=True)

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ChangeManagerView(APIView):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOperationPermission]

    def put(self, request):
        update_user_list=[]
        newManager_id = request.query_params.get('newManager_id', None)

        if newManager_id is None:
            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Next Manager ID is required in the request Params.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not newManager_id.isdigit():
            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': "'newManager_id' expected a number but got other."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            nextManager = CustomUser.objects.get(id=newManager_id)
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'status': 404,
                'message': 'Next manager not found.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            currentManager = CustomUser.objects.get(id=request.user.id)
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'status': 404,
                'message': 'Current manager not found.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if nextManager.is_manager:
            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Selected user is already a manager'
            }, status=status.HTTP_400_BAD_REQUEST)
        # Change Manager ship
        if nextManager.is_superuser:
            return Response({
                'success': False,
                'status': 403,
                'message': 'Superuser cannot be a Manager'
            }, status=status.HTTP_403_FORBIDDEN)
        # Change Manager ship
        if currentManager.id != nextManager.id:
            # Update is_staff attribute using the serializer

            if currentManager.is_superuser:
                searchManager = CustomUser.objects.filter(is_staff=True, is_manager=True).first()

                if searchManager is not None:
                        nextManager_serializer = ChangeManagerSerializer(nextManager, {'is_staff': True, 'is_manager': True,'role': 'manager'}, partial=True)
                        nextManager_serializer.is_valid(raise_exception=True)
                        nextManager_serializer.save()
                        managersData= UserProfileSerializer(nextManager).data
                        update_user_list.append(managersData)

                        currentManager_serializer = ChangeManagerSerializer(searchManager, {'is_staff': False, 'is_manager': False,'role': 'member'}, partial=True)
                        currentManager_serializer.is_valid(raise_exception=True)
                        currentManager_serializer.save()
                        managersData= UserProfileSerializer(searchManager).data
                        update_user_list.append(managersData)
                        return Response({
                            'success': True,
                            'status': status.HTTP_200_OK,
                            'message': 'Manager changed successfully',
                            'data': update_user_list
                        }, status=status.HTTP_200_OK)
                else:
                    nextManager_serializer = ChangeManagerSerializer(nextManager, {'is_staff': True, 'is_manager': True,'role': 'manager'}, partial=True)
                    nextManager_serializer.is_valid(raise_exception=True)
                    nextManager_serializer.save()
                    managersData= UserProfileSerializer(nextManager).data
                    update_user_list.append(managersData)
                    return Response({
                            'success': True,
                            'status': status.HTTP_200_OK,
                            'message': 'Manager changed successfully',
                            'data': update_user_list
                        }, status=status.HTTP_200_OK)
                
            
            nextManager_serializer = ChangeManagerSerializer(nextManager, {'is_staff': True, 'is_manager': True,'role': 'manager'}, partial=True)
            nextManager_serializer.is_valid(raise_exception=True)
            nextManager_serializer.save()
            managersData= UserProfileSerializer(nextManager).data
            update_user_list.append(managersData)

            currentManager_serializer = ChangeManagerSerializer(currentManager, {'is_staff': False, 'is_manager': False,'role': 'member'}, partial=True)
            currentManager_serializer.is_valid(raise_exception=True)
            currentManager_serializer.save()
            managersData= UserProfileSerializer(currentManager).data
            update_user_list.append(managersData)
            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'Manager changed successfully',
                'data': update_user_list
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Selected user is already a manager'
            }, status=status.HTTP_400_BAD_REQUEST)


class AllUserListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        try:
            # Check if the requesting user is a superuser
            if request.user.is_superuser:
                # Retrieve all users from the database
                active_users = CustomUser.objects.all()
            else:
                # Retrieve only the current user's data
                active_users = CustomUser.objects.filter(is_superuser=False)

            # Serialize the active users
            serializer = AllUserListSerializer(active_users, many=True)

            # Return the serialized data in the response
            return Response({
                    'success': True,
                    'status': status.HTTP_200_OK,
                    'message': 'Successfully retrieved all users',
                    'data': serializer.data,
                })
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': f'An error occurred while processing the request: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
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


                


