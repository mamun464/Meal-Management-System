from django.urls import path

from account.views import UserLoginView
from HostelApp.views import MonthlyMealView,MealRateView,MealEntryView

urlpatterns = [
    path('all-meal-monthly/', MonthlyMealView.as_view(),name='all-meal-monthly'),
    path('meal-rate/', MealRateView.as_view(),name='meal-rate'),
    path('meal-entry/', MealEntryView.as_view(),name='meal-entry'),
 
    
]