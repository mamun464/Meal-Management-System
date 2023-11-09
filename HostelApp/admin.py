from django.contrib import admin
from .models import MealHistory,BazarHistory
# Register your models here.

class MealHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'date', 'lunch', 'dinner', 'meal_sum_per_day')
    list_filter = ('date',)


class BazarHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'date','daily_bazar_cost','bazar_details','user' )
    

admin.site.register(MealHistory,MealHistoryAdmin)
admin.site.register(BazarHistory,BazarHistoryAdmin)
