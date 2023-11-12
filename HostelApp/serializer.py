
from rest_framework import serializers
from .models import MealHistory,BazarHistory,CustomUser,ExtraExpensesHistory,UserPaymentHistory

class MonthlyMealSerializer(serializers.ModelSerializer):
    class Meta:
        model= MealHistory
        fields = ('year', 'month') # I added the fields accept in the JSON data 


#Need to Impliment
class MealRateSerializer(serializers.ModelSerializer):
    pass


class MealEntrySerializer(serializers.ModelSerializer):
   class Meta:
        model = MealHistory
        fields = ('user', 'date', 'lunch', 'dinner')


class MealEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealHistory
        fields = ('date', 'user', 'lunch', 'dinner')

class MonthlySingleUserDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = MealHistory
        fields = ('id','date', 'user',  'lunch', 'dinner', 'meal_sum_per_day')



class BazarEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BazarHistory
        fields = ['user', 'date', 'daily_bazar_cost', 'bazar_details']

class AllBazarListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BazarHistory
        fields = ['date', 'daily_bazar_cost', 'bazar_details','user']


class ExtraExpensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraExpensesHistory
        fields = [ 'date', 'expense_name', 'expense_amount']

class AllExtraExpenseSerializer(serializers.ModelSerializer): 
        class Meta:
            model = ExtraExpensesHistory
            fields = [ 'id','date', 'expense_name', 'expense_amount']


