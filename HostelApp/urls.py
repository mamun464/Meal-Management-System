from django.urls import path

from account.views import UserLoginView
from HostelApp.views import MonthlyMealView,MealRateView,MealEntryView,MealEditView,MonthlySingleUserDetailsView,BazarEntryView,AllBazarListView,MonthlyAllUserDetailsView,ExtraExpensesView,AllExtraExpenseView

urlpatterns = [
    path('all-meal-monthly/', MonthlyMealView.as_view(),name='all-meal-monthly'),
    path('meal-rate/', MealRateView.as_view(),name='meal-rate'),
    path('meal-entry/', MealEntryView.as_view(),name='meal-entry'),
    path('meal-edit/', MealEditView.as_view(),name='meal-edit'),
    path('monthly-user-details/', MonthlySingleUserDetailsView.as_view(),name='monthly-user-details'),
    path('bazar-entry/', BazarEntryView.as_view(),name='bazar-entry'),
    path('monthly-allbazar-list/', AllBazarListView.as_view(),name='monthly-allbazar-list'),
    path('monthly-all-user-details/', MonthlyAllUserDetailsView.as_view(),name='monthly-all-user-details'),
    path('extra-expense-entry/', ExtraExpensesView.as_view(),name='extra-expense-entry'),
    path('monthly-extra-expense-list/', AllExtraExpenseView.as_view(),name='extra-expense-view'),
    path('edit-extra-expense/', AllExtraExpenseView.as_view(),name='extra-expense-edit'),
    path('delete-expense/', AllExtraExpenseView.as_view(),name='extra-expense-delete'),
 
    
]