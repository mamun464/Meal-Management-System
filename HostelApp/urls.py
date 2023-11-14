from django.urls import path

from account.views import UserLoginView
from HostelApp.views import MonthlyMealView,MealRateView,MealEntryView,MealEditView,MonthlySingleUserDetailsView,BazarEntryView,AllBazarListView,MonthlyAllUserDetailsView,ExtraExpensesView,AllExtraExpenseView,PaymentEntryView,AvailabilityCheckView

urlpatterns = [

    #Meal Operations 
    path('all-meal-monthly/', MonthlyMealView.as_view(),name='all-meal-monthly'),
    path('meal-rate/', MealRateView.as_view(),name='meal-rate'),
    path('meal-entry/', MealEntryView.as_view(),name='meal-entry'),
    path('meal-edit/', MealEditView.as_view(),name='meal-edit'),
    path('monthly-user-details/', MonthlySingleUserDetailsView.as_view(),name='monthly-user-details'),
    path('monthly-all-user-details/', MonthlyAllUserDetailsView.as_view(),name='monthly-all-user-details'),

    #Bazar Oparation
    path('bazar-entry/', BazarEntryView.as_view(),name='bazar-entry'),
    path('monthly-allbazar-list/', AllBazarListView.as_view(),name='monthly-allbazar-list'),
    path('edit-bazar/', AllBazarListView.as_view(),name='bazar-edit'),
    path('delete-bazar/', AllBazarListView.as_view(),name='delete-bazar'),
   
    #Extra Expenses Oaration
    path('extra-expense-entry/', ExtraExpensesView.as_view(),name='extra-expense-entry'),
    path('monthly-extra-expense-list/', AllExtraExpenseView.as_view(),name='extra-expense-view'),
    path('edit-extra-expense/', AllExtraExpenseView.as_view(),name='extra-expense-edit'),
    path('delete-expense/', AllExtraExpenseView.as_view(),name='extra-expense-delete'),

    #Balance Operation
    path('payment-entry/', PaymentEntryView.as_view(),name='payment-entry'),
    path('monthly-payment-data/', PaymentEntryView.as_view(),name='monthly-payment-data'),
    path('edit-payment/', PaymentEntryView.as_view(),name='edit-payment'),
    path('delete-payment/', PaymentEntryView.as_view(),name='payment-delete'),
    
    #availability check API methods
    path('availability-check/', AvailabilityCheckView.as_view(), name='availability_check_api'),
 
    
]