from django.urls import path

from account.views import UserLoginView
from HostelApp.views import MonthlyMealView,MealRateView

urlpatterns = [
    path('all-meal-monthly/', MonthlyMealView.as_view(),name='all-meal-monthly'),
    path('meal-rate/', MealRateView.as_view(),name='meal-rate'),
 
    
]