from django.urls import path

from account.views import UserLoginView
from HostelApp.views import MonthlyMealView,MealRateView,MealEntryView,MealEditView,MonthlySingleUserDetailsView

urlpatterns = [
    path('all-meal-monthly/', MonthlyMealView.as_view(),name='all-meal-monthly'),
    path('meal-rate/', MealRateView.as_view(),name='meal-rate'),
    path('meal-entry/', MealEntryView.as_view(),name='meal-entry'),
    path('meal-edit/', MealEditView.as_view(),name='meal-edit'),
    path('monthly-user-details/', MonthlySingleUserDetailsView.as_view(),name='monthly-user-details'),
 
    
]