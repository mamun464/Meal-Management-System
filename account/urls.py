
# from django.contrib import admin
from django.urls import path

from account.views import UserRegistrationView,UserLoginView,UserProfileView,UserPasswordChangeView,SendPasswordResetEmailView,UserPasswordResetView,UserDeleteView,UserEditView,LogoutAPIView,ChangeManagerView,AllUserListView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(),name='register'),
    path('login/', UserLoginView.as_view(),name='login'),
    path('profile/', UserProfileView.as_view(),name='profile'),
    path('changepassword/', UserPasswordChangeView.as_view(),name='passwordChange'),
    path('send-rest-password-email/', SendPasswordResetEmailView.as_view(),name='send-rest-password-email'),
    path('rest-password/<uid>/<token>/', UserPasswordResetView.as_view(),name='rest-password'),
    path('delete/<phone>/', UserDeleteView.as_view(),name='delete-user'),
    path('update/', UserEditView.as_view(),name='edit-user'),
    path('logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('managership/', ChangeManagerView.as_view(), name='change-manager'),
    path('user-list/', AllUserListView.as_view(), name='user-list'),
    
    
]
