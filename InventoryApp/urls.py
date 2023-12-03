
# from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from InventoryApp.views import ItemCreateView

urlpatterns = [
    path('create-item/', ItemCreateView.as_view(),name='create-item'),

]