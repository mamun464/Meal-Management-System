from django.contrib import admin
from .models import MealHistory
# Register your models here.

class MealHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'date', 'lunch', 'dinner', 'meal_sum_per_day')
    #list_filter = ('user', 'date__year', 'date__month')
    

admin.site.register(MealHistory,MealHistoryAdmin)
