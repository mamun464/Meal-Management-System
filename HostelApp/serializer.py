
from rest_framework import serializers
from .models import MealHistory

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

