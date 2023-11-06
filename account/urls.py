
# from django.contrib import admin
from django.urls import path,include
from account.views import UserRegistrationView,UserLoginView,UserProfileView,UserPasswordChangeView,SendPasswordResetEmailView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(),name='register'),
    path('login/', UserLoginView.as_view(),name='login'),
    path('profile/', UserProfileView.as_view(),name='profile'),
    path('changepassword/', UserPasswordChangeView.as_view(),name='passwordChange'),
    path('send-rest-password-email/', SendPasswordResetEmailView.as_view(),name='send-rest-password-email'),
    
]
