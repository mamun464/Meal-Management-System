from django.shortcuts import render
from rest_framework.views import APIView
from account.renderers import UserRenderer
from HostelApp.serializer import MonthlyMealSerializer,MealEntrySerializer,MealEditSerializer,MonthlySingleUserDetailsSerializers,BazarEntrySerializer,AllBazarListSerializer
from account.serializer import UserProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import MealHistory,CustomUser,BazarHistory
from django.db.models import Sum
from HostelApp.Calculationhelper import CallMonthlyTotalMealAPI,CallMealRateAPI,CallBazarListAPI
import math
import datetime

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

    def post(self, request):
        
        monthly_total_bazar_cost =0
        
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        Total_meal_response=CallMonthlyTotalMealAPI(year=year, month=month)
        bazar_List_response=CallBazarListAPI(year=year, month=month)
        #return Response(Total_meal_monthly['success'], status=status.HTTP_200_OK)

        if bazar_List_response['success']:
            allBazarObject=bazar_List_response['data']
            datewise_bazar=allBazarObject['data']
            for eachBazar in datewise_bazar:
                eachBazarCost= eachBazar['daily_bazar_cost']
                monthly_total_bazar_cost += float(eachBazarCost)
                
        else:
            # print("Error came form Bazar list Else")
            return Response(bazar_List_response, status=status.HTTP_400_BAD_REQUEST)
        

        if Total_meal_response['success'] :
            Total_meal_monthly=Total_meal_response['data']['Total Meal']

            # print(type(Total_meal_monthly))

            if Total_meal_monthly > 0:
                meal_rate = monthly_total_bazar_cost/Total_meal_monthly
                meal_rate_rounded = round(meal_rate,2)
                msg = {
                    'Meal_Rate': meal_rate_rounded,
                    
                }
                return Response(msg, status=status.HTTP_200_OK)
            
            else:
                msg ={
                    'Meal_Rate':0
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
    

class MealEditView(APIView):
    renderer_classes = [UserRenderer]
    def put(self, request):
        user_id = request.data.get('user_id', None)
        date = request.data.get('date', None)
        lunch = request.data.get('lunch')
        dinner = request.data.get('dinner')

        # Validate the date format
        try:
            meal_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Date must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

        if user_id is None or date is None:
            return Response({'error': 'userId and date are required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)
        
                # Check that at least one of lunch or dinner is provided
        if lunch is None and dinner is None:
            return Response({'error': 'At least one of lunch or dinner must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            meal_entry = MealHistory.objects.get(user_id=user_id, date=meal_date)
        except MealHistory.DoesNotExist:
            return Response({'error': 'Meal entry not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = MealEditSerializer(meal_entry, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Successfully Edited Meal.','data':serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class MonthlySingleUserDetailsView(APIView):
    renderer_classes = [UserRenderer]
    def get(self, request):
        user_id = request.query_params.get('user')
        year = request.query_params.get('year', None)
        month = request.query_params.get('month', None)

        
        if not user_id or not year or not month:
            return Response({'error': 'user, year, and month are required query parameters.'}, status=400)
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response({'error': 'Year and month must be valid integers.'}, status=400)
        

        
        # Check if year is within a valid range
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        if year < 1900 or year > current_year:
            return Response({'error': 'Year is out of range.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if month is within a valid range (1 to 12)
        if month < 1 or month > 12 or current_month < month:
            return Response({'error': 'Month is out of range.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user instance from the CustomUser model
        try:
            user = CustomUser.objects.get(id=user_id)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        
        
        bazar_List_response=CallBazarListAPI(year=year, month=month)
        #return Response(Total_meal_monthly['success'], status=status.HTTP_200_OK)

        #user wise bazar count
        going_for_bazar=0
        if bazar_List_response['success']:
            allBazarObject=bazar_List_response['data']
            datewise_bazar=allBazarObject['data']
            for eachBazar in datewise_bazar:
                user_id_in_bazar= eachBazar['user']
                if user_id_in_bazar == int(user_id):
                    going_for_bazar += 1
                

        # Filter MealHistory entries for the specific user, year, and month
        meal_entries = MealHistory.objects.filter(
            user_id=user_id,
            date__year=year,
            date__month=month
        )
        # Include user details in the response
        user_details = {
            'user_id': user.id,
            'fullName': user.fullName,
            'email': user.email,
            'phone_no': user.phone_no,
        }

        meal_serializer = MonthlySingleUserDetailsSerializers(meal_entries, many=True)

        meal_rate_response = CallMealRateAPI(year=year, month=month)
        
        meal_rate_floot=0
        if meal_rate_response['success']: 
            meal_rate_floot = meal_rate_response['data']['Meal_Rate']

        

        MonthlyDateWiseMeal =  meal_serializer.data
        monthly_total_meal_single_user=0
        if len(MonthlyDateWiseMeal) != 0:
            for eachDayMeal in MonthlyDateWiseMeal:
                monthly_total_meal_single_user+=float(eachDayMeal['meal_sum_per_day'])

        meal_cost_monthly= round((meal_rate_floot * monthly_total_meal_single_user),2)

        response_data = {
            'user_details': user_details,
            'user_accounts':{
                'going_for_bazar': going_for_bazar,
                'total_meal_monthly' : monthly_total_meal_single_user,
                'total_taka_submit': 'Coming Soon',
                'extra_cost': 'Coming Soon',
                # 'real_rate2' : meal_rate_floot,#meal_rate_response,
                'real_rate' : meal_rate_response,
                'meal_cost_monthly': meal_cost_monthly,
                'remain_balance' : 'Coming Soon',
                'due' : 'Coming Soon',
            },
            'access_permissions':"Coming Soon",
            'date_wise_meal': MonthlyDateWiseMeal,
        }

        # Serialize the data

        return Response(response_data,status=status.HTTP_200_OK)
    


class BazarEntryView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request):
        try:
            # Get the phone number from the request data
            phone_no = request.data['phone_no']
            bazar_cost=request.data['daily_bazar_cost']
            date = request.data['date']

            # Get the user ID using the phone number
            user = CustomUser.objects.get(phone_no=phone_no)
            user_id = user.id
        except CustomUser.DoesNotExist:
            return Response({'error':{'message': f'User with phone number {phone_no} not found'}})
        except Exception as e:
            return Response({'error':{'message': f'An unexpected error occurred: {e}'}})
        # Handle the optional bazar_details field
        bazar_details = request.data.get('bazar_details', None)
        # Create the BazarHistory instance
        bazar_history_data = {
            'user': user_id,
            'date': date,
            'daily_bazar_cost': bazar_cost,
            'bazar_details': bazar_details,
        }
        serializer = BazarEntrySerializer(data=bazar_history_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a success response
        return Response({'status': 'Bazar Entry successful'})
    
class AllBazarListView(APIView):
    renderer_classes = [UserRenderer]
    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if not year or not month:
            return Response({'error': 'year, and month are required query parameters.'}, status=400)

        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response({'error': 'Year and month must be valid integers.'}, status=400)
        
        # Check if year is within a valid range
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        if year < 1900 or year > current_year:
            return Response({'error': 'Year is out of range.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if month is within a valid range (1 to 12)
        if month < 1 or month > 12 or current_month < month:
            return Response({'error': 'Month is out of range.'}, status=status.HTTP_400_BAD_REQUEST)


        # Filter MealHistory entries for the specific user, year, and month
        bazar_entries = BazarHistory.objects.filter(
            date__year=year,
            date__month=month
        )

        bazar_serializer = AllBazarListSerializer(bazar_entries, many=True)
        return Response({'Success':True,'data':bazar_serializer.data},status=status.HTTP_200_OK)
    

class MonthlyAllUserDetailsView(APIView):
    pass