from django.shortcuts import render
from rest_framework.views import APIView
from account.renderers import UserRenderer
from HostelApp.serializer import MonthlyMealSerializer,MealEntrySerializer
from rest_framework.response import Response
from rest_framework import status
from .models import MealHistory
from django.db.models import Sum
from HostelApp.Calculationhelper import CallMonthlyTotalMealAPI
import math

# Create your views here.
class MonthlyMealView(APIView):
    
    renderer_classes = [UserRenderer]
    def post(self, request):
        year = request.data.get('year', None)
        month = request.data.get('month', None)

        if year is None or month is None or not year.isdigit() or not month.isdigit():
            return Response({'error': 'Valid year and month are required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)

        year = int(year)
        month = int(month)

        total_meal_sum = MealHistory.objects.filter(
            date__year=year,
            date__month=month
        ).aggregate(
            total_sum=Sum('meal_sum_per_day')
        )['total_sum'] or 0

        total_meal_sum = float(total_meal_sum)

        response_data = {
            'year': year,
            'month': month,
            'Total Meal': total_meal_sum,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    


class MealRateView(APIView):

    def get(self, request):
        monthly_meal_total_expenses =2000
        year='2023'
        month='11'
        Total_meal_response=CallMonthlyTotalMealAPI(year=year, month=month)
        #return Response(Total_meal_monthly['success'], status=status.HTTP_200_OK)

        if Total_meal_response['success'] :
            Total_meal_monthly=Total_meal_response['data']['Total Meal']

            print(type(Total_meal_monthly))

            if Total_meal_monthly > 0:
                meal_rate = monthly_meal_total_expenses/Total_meal_monthly
                meal_rate_rounded = round(meal_rate,2)
                msg = {
                    'Meal_Rate': meal_rate_rounded,
                    
                }
                return Response(msg, status=status.HTTP_200_OK)
            
            else:
                msg ={
                    'Meal_Rate':'No Meal Available'
                    }

                return Response(msg, status=status.HTTP_200_OK)
            
            
        else:

            return Response(Total_meal_response, status=status.HTTP_400_BAD_REQUEST)

class MealEntryView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = MealEntrySerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            mealEntry = serializer.save()
            return Response({'msg':'Successfully added Meal'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)