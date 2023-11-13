from django.contrib import admin
from .models import MealHistory,BazarHistory,UserPaymentHistory, ExtraExpensesHistory
# Register your models here.

class MealHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'date', 'lunch', 'dinner', 'meal_sum_per_day')
    list_filter = ('date',)


class BazarHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'date','daily_bazar_cost','bazar_details','user' )


class UserPaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'date', 'submitted_amount')
    search_fields = ('user__email', 'user__phone_no', 'date')
    list_filter = ('user__email', 'user__phone_no', 'date')

class ExtraExpensesHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','date', 'expense_name', 'expense_amount')
    search_fields = ('date', 'expense_name')
    list_filter = ('date', 'expense_name')
    

admin.site.register(MealHistory,MealHistoryAdmin)
admin.site.register(BazarHistory,BazarHistoryAdmin)
admin.site.register(UserPaymentHistory, UserPaymentHistoryAdmin)
admin.site.register(ExtraExpensesHistory, ExtraExpensesHistoryAdmin)
