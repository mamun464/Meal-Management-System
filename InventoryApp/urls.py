
# from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from InventoryApp.views import ItemView

urlpatterns = [
    path('create-item/', ItemView.as_view(),name='create-item'),
    path('get-item/', ItemView.as_view(),name='get-item'),
    path('update-item/', ItemView.as_view(),name='get-item'),
    path('delete-item/', ItemView.as_view(),name='get-item'),

]