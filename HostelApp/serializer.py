
from rest_framework import serializers
from .models import MealHistory

class MonthlyMealSerializer(serializers.ModelSerializer):
    class Meta:
        model= MealHistory
        fields = ('year', 'month') # I added the fields accept in the JSON data 


class MealRateSerializer(serializers.ModelSerializer):
    pass