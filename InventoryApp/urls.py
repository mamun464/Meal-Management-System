
# from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from InventoryApp.views import ItemView,ItemInventoryView,DamageAdd,GetItemVariant,GetUniqueItemNames,SingleInventoryView,StockView,CreateInvoiceView,GenerateInvoice

urlpatterns = [
    # Iteam Table
    path('create-item/', ItemView.as_view(),name='create-item'),
    path('get-item/', ItemView.as_view(),name='get-item'),
    path('single-item/', ItemView.as_view(),name='get-single-item'),
    path('update-item/', ItemView.as_view(),name='update-item'),
    path('delete-item/', ItemView.as_view(),name='delete-item'),
    path('get-item-variant/', GetItemVariant.as_view(), name='get-item-variant'),
    path('unique-item-names/', GetUniqueItemNames.as_view(), name='get-unique-item-names'),

    # itemInventory
    path('create-invoice/', CreateInvoiceView.as_view(),name='create-invoice'),
    path('add-inventory/', ItemInventoryView.as_view(),name='add-inventory'),
    path('get-inventory/', ItemInventoryView.as_view(),name='get-inventory'),
    path('single-inventory/', SingleInventoryView.as_view(),name='single-inventory'),
    path('update-inventory/', ItemInventoryView.as_view(),name='update-inventory'),
    path('add-damage/', DamageAdd.as_view(),name='add-damage'),
    path('delete-inventory/', ItemInventoryView.as_view(),name='delete-item'),
    path('stock/', StockView.as_view(),name='stock'),

    path('generateinvoice/', GenerateInvoice.as_view(), name = 'generateinvoice'),




]