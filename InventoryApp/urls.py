
# from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from InventoryApp.views import ItemView,ItemInventoryView,DamageAdd,GetItemVariant

urlpatterns = [
    # Iteam Table
    path('create-item/', ItemView.as_view(),name='create-item'),
    path('get-item/', ItemView.as_view(),name='get-item'),
    path('single-item/', ItemView.as_view(),name='get-single-item'),
    path('update-item/', ItemView.as_view(),name='update-item'),
    path('delete-item/', ItemView.as_view(),name='delete-item'),
    path('get-item-variant/', GetItemVariant.as_view(), name='get-item-variant'),

    # itemInventory
    path('add-inventory/', ItemInventoryView.as_view(),name='add-inventory'),
    path('get-inventory/', ItemInventoryView.as_view(),name='get-inventory'),
    path('update-inventory/', ItemInventoryView.as_view(),name='update-inventory'),
    path('add-damage/', DamageAdd.as_view(),name='add-damage'),
    path('delete-inventory/', ItemInventoryView.as_view(),name='delete-item'),




]