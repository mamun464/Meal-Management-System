from django.shortcuts import render
from rest_framework.views import APIView
from account.renderers import UserRenderer
from HostelApp.serializer import MonthlyMealSerializer,MealEntrySerializer,MealEditSerializer,MonthlySingleUserDetailsSerializers,BazarEntrySerializer,AllBazarListSerializer,ExtraExpensesSerializer,AllExtraExpenseSerializer,PaymentEntrySerializer
from account.serializer import UserProfileSerializer
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import MealHistory,CustomUser,BazarHistory,ExtraExpensesHistory,UserPaymentHistory,UserAvailabilityCheck
from django.db.models import Sum
from HostelApp.Calculationhelper import CallMonthlyTotalMealAPI,CallMealRateAPI,CallBazarListAPI,CallMonthlySingleUserDetailsAPI,CallExtraCostAPI,CallPaymentListAPI
from django.db.models import Q
import datetime as dt_datetime
# from datetime import datetime as dt_datetime, date as dt_date
from datetime import datetime, date
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication


from django.core.serializers.json import DjangoJSONEncoder





# All calculation doing here for  a single user
class UserDetailsMixin:
    def get_user_data(self, user, request):
        # Your existing logic for MonthlySingleUserDetailsView

        year = request.query_params.get('year', None)
        month = request.query_params.get('month', None)
        # ...
        bazar_List_response=CallBazarListAPI(year=year, month=month)

        extra_expense_List_response=CallExtraCostAPI(year=year, month=month)

        # print("Upper payment_List_response")

        payment_List_response=CallPaymentListAPI(year=year, month=month)

        #Submitted Amount Calculations
        total_pay_amount= 0
        meal_account_balance= 0
        total_pay_history= []
        if payment_List_response['data']['Success']:
            list_of_all_payment = payment_List_response['data']['data']
            for eachPayment in list_of_all_payment:
                meal_account_balance+= float(eachPayment['submitted_amount'])
                if eachPayment['user'] == user.id:
                    total_pay_history.append(eachPayment)
                    total_pay_amount+= float(eachPayment['submitted_amount'])
        else:
            return("No data found")

        
        #return Response(Total_meal_monthly['success'], status=status.HTTP_200_OK)

        #user wise bazar count
        going_for_bazar=0
        if bazar_List_response['success']:
            allBazarObject=bazar_List_response['data']
            datewise_bazar=allBazarObject['data']
            for eachBazar in datewise_bazar:
                # total_bazar_cost_monthly += eachBazar['data
                user_id_in_bazar= eachBazar['user']
                if user_id_in_bazar == user.id:
                    going_for_bazar += 1



    #    extra Expenses calculations
        totall_monthly_extra_expense=0
        if extra_expense_List_response['success']:
            allExpenseObject=extra_expense_List_response['data']
            datewise_expese=allExpenseObject['data']
            for eachExpese in datewise_expese:
                    totall_monthly_extra_expense += float(eachExpese['expense_amount'])

        

        # Counting all non-superuser users based on conditions
        person_in_month = CustomUser.objects.filter(

            (Q(is_active=True) | Q(availability_check__is_available=True)) & ~Q(is_superuser=True),
            availability_check__month=month,
            availability_check__year=year,

        ).distinct().count()

        # Avoid division by zero
        per_head_extra_cost =round((totall_monthly_extra_expense / person_in_month), 2) if person_in_month != 0 else 0

        cost_data={
            "total_extra_cost":totall_monthly_extra_expense,
             "Active_User" : person_in_month,
             "extra_cost_per_head" : per_head_extra_cost,

            "datewise_expese":datewise_expese,
           
        }

        # Filter MealHistory entries for the specific user, year, and month
        meal_entries = MealHistory.objects.filter(
            user_id=user.id,
            date__year=year,
            date__month=month
        )
        # Include user details in the response
        user_details = {
            'user_id': user.id,
            'fullName': user.fullName,
            'profile_img': user.user_profile_img.url if user.user_profile_img else None,
            'email': user.email,
            'phone_no': user.phone_no,
            'last_login': user.last_login,
            'last_login': self.serialize_datetime(user.last_login),
        }

        permissions ={
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_manager': user.is_manager,
            'is_superuser': user.is_superuser,
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

        # remaining Balance calculations
        remaining_balance = round(total_pay_amount - (meal_cost_monthly+cost_data['extra_cost_per_head']),2)
        if remaining_balance < 0:
            show_remaining_balance = 0
            due_balance = remaining_balance*(-1)
        else:
            show_remaining_balance=remaining_balance
            due_balance = 0

        response_data = {
            'user_details': {
                 **user_details,
                'access_permissions': permissions,
                },
            'user_accounts':{
                'going_for_bazar': going_for_bazar,
                'total_meal_monthly' : monthly_total_meal_single_user,
                'total_taka_submit': total_pay_amount,
                'extra_cost': cost_data,
                # 'real_rate2' : meal_rate_floot,#meal_rate_response,
                'real_rate' : meal_rate_response,
                'meal_cost_monthly': meal_cost_monthly,
                'remain_balance' : show_remaining_balance,
                'due' : due_balance,
                'payment_history' : total_pay_history,
            },
           
            'date_wise_meal': MonthlyDateWiseMeal,
        }

        return response_data

        # Instead of returning the Response, return the data
    def serialize_datetime(self, datetime_obj):
            if datetime_obj is not None:
                return DjangoJSONEncoder().encode(datetime_obj).strip('"')
            return None


# Create your views here.
class MonthlyMealView(APIView):
    
    renderer_classes = [UserRenderer]
    def post(self, request):
        year = request.query_params.get('year', None)
        month = request.query_params.get('month', None)

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        serializer = MealEntrySerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'msg': 'Successfully added Meal'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Check if the user is active before saving the meal entry
        user = serializer.validated_data['user']

        if not user.is_active:
            raise serializers.ValidationError({'user': 'User is not active for this month.'})

        serializer.save()
    

class MealEditView(APIView):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    def put(self, request):
        user_id = request.data.get('user_id', None)
        date = request.data.get('date', None)
        lunch = request.data.get('lunch')
        dinner = request.data.get('dinner')

        # Validate the date format
        try:
            meal_date = dt_datetime.datetime.strptime(date, '%Y-%m-%d').date()
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
    

class MonthlySingleUserDetailsView(APIView,UserDetailsMixin):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
       
        year = request.query_params.get('year', None)
        month = request.query_params.get('month', None)
        user_id = request.query_params.get('user_id', None)

        
        if not year or not month or not user_id:
            return Response({'error': 'user, year, and month are required query parameters.'}, status=400)
        try:
            year = int(year)
            month = int(month)
            user_id =int(user_id)
        except ValueError:
            return Response({'error': 'User Id, Year and month must be valid integers.'}, status=400)
        

        
        # Check if year is within a valid range
        current_year = dt_datetime.datetime.now().year
        current_month = dt_datetime.datetime.now().month
        if year < 1900 or year > current_year:
            return Response({'Year Must be valid Or not greater than current year.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if month is within a valid range (1 to 12)
        if month < 1 or month > 12 or (current_year == year and current_month < month):
            return Response({'error': 'Month Must have Valid Month or must request less that current month'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user instance from the CustomUser model
        try:
            user = CustomUser.objects.get(id=user_id)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        
        

        response_data = self.get_user_data(user, request)
        # response_data={'user': response_data}
        # Serialize the data
        return Response(response_data, status=status.HTTP_200_OK)
    


class BazarEntryView(APIView):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = []
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
        current_year = dt_datetime.datetime.now().year
        current_month = dt_datetime.datetime.now().month
        if year < 1900 or year > current_year:
            return Response({'error': 'Year Must be valid Or not greater than current year.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if month is within a valid range (1 to 12)
        if month < 1 or month > 12 or (current_year == year and current_month < month):
            return Response({'error': 'Month Must have Valid Month or must request less that current month'}, status=status.HTTP_400_BAD_REQUEST)


        # Filter MealHistory entries for the specific user, year, and month
        bazar_entries = BazarHistory.objects.filter(
            date__year=year,
            date__month=month
        )

        bazar_serializer = AllBazarListSerializer(bazar_entries, many=True)
        return Response({'Success':True,'data':bazar_serializer.data},status=status.HTTP_200_OK)
    
    def put(self, request):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)

        bazar_id = request.query_params.get('bazar_id', None)
        # user_id = request.query_params.get('user', None)

        if bazar_id is None : #or user_id is None
            return Response({'error': 'Bazar ID required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not bazar_id.isdigit() : #or not user_id.isdigit()
            return Response({'error':  " 'id' expected a number but got other"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            bazar_entry = BazarHistory.objects.get(id=bazar_id)
            # user = CustomUser.objects.get(id=user_id, is_active=True)
        except BazarHistory.DoesNotExist:
            return Response({'error': 'Bazar entry not found.'}, status=status.HTTP_404_NOT_FOUND)
        # except CustomUser.DoesNotExist:
        #     return Response({'error': 'User not found. May be not active user'}, status=status.HTTP_404_NOT_FOUND)


        serializer = AllBazarListSerializer(bazar_entry, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Successfully Edited Bazar.','data':serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        # IsAdminUser applited
        # self.permission_classes = [IsAdminUser]
        self.renderer_classes = [UserRenderer]
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)

        bazar_id = request.query_params.get('bazar_id', None)

        if bazar_id is None :
            return Response({'error': 'Expense ID are required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not bazar_id.isdigit():
            return Response({'error':  f" 'id' expected a number but got {bazar_id}"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            bazar_entry = BazarHistory.objects.get(id=bazar_id)
        except BazarHistory.DoesNotExist:
            return Response({'error': 'Bazar Expense entry not found.'}, status=status.HTTP_404_NOT_FOUND)
            

        bazar_entry.delete()
        return Response({'msg': f'{bazar_id} No. Bazar -Deleted from your system'},status=status.HTTP_204_NO_CONTENT)
    

class MonthlyAllUserDetailsView(APIView,UserDetailsMixin):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    def get(self, request):
       
        year = request.query_params.get('year', None)
        month = request.query_params.get('month', None)

        
        if  not year or not month:
            return Response({'error': 'user, year, and month are required query parameters.'}, status=400)
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response({'error': 'Year and month must be valid integers.'}, status=400)
        

        
        # Check if year is within a valid range
        current_year = dt_datetime.datetime.now().year
        current_month = dt_datetime.datetime.now().month
        if year < 1900 or year > current_year:
            return Response({'error':'Year Must be valid Or not greater than current year.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if month is within a valid range (1 to 12)
        if month < 1 or month > 12 or (current_year == year and current_month < month):
            
            return Response({'error': 'Month Must have Valid Month or must request less that current month'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the user instance from the CustomUser model
        
        allUserID= list(CustomUser.objects.values_list('id', flat=True).order_by('id'))

        MonthlyAllUser=[]

        for user_id in allUserID:
            # singleUser = CallMonthlySingleUserDetailsAPI(user_id,year, month)
            # MonthlyAllUser.append(singleUser)
            # print(user_id, "Type: " , type(user_id))
            try:
                user = CustomUser.objects.get(id=user_id)

            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found.'}, status=404)
            
            user_data = self.get_user_data(user, request)
            MonthlyAllUser.append(user_data)
        
        return Response({'Success': True,
                         'data': MonthlyAllUser}, status=status.HTTP_200_OK)
    
class ExtraExpensesView(APIView):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    def post(self, request):
        try:
            # Get the phone number from the request data
            get_date = request.data['date']
            get_expense_name=request.data['expense_name']
            get_expense_amount=request.data['expense_amount']

            # date convertin date format
            get_date = datetime.strptime(get_date, '%Y-%m-%d').date()

            today = date.today()
            if get_date > today:
                return Response({"error": "Date cannot be greater than today"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error':{'message': f'An unexpected error occurred: {e}'}},status=status.HTTP_400_BAD_REQUEST)
        
        # Create the extra_expense_amount instance
        extra_expense_data = {

            'date': get_date,
            'expense_name': get_expense_name,
            'expense_amount': get_expense_amount,
        }
        serializer = ExtraExpensesSerializer(data=extra_expense_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a success response
        return Response({'status': 'Extra Expenses Entry successful'},status=status.HTTP_201_CREATED)
    

class AllExtraExpenseView(APIView):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = []
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
        current_year = dt_datetime.datetime.now().year
        current_month = dt_datetime.datetime.now().month
        if year < 1900 or year > current_year:
            return Response({'error': 'Year Must be valid Or not greater than current year.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if month is within a valid range (1 to 12)
        if month < 1 or month > 12 or (current_year == year and current_month < month):
            return Response({'error': 'Month Must have Valid Month or must request less that current month (Testing)'}, status=status.HTTP_400_BAD_REQUEST)


        # Filter Extra Expenses entries for the specific, year, and month
        extra_expense_entries = ExtraExpensesHistory.objects.filter(
            date__year=year,
            date__month=month
        )

        extra_expenses_serializer = AllExtraExpenseSerializer(extra_expense_entries, many=True)

        return Response({'Success':True,'data':extra_expenses_serializer.data},status=status.HTTP_200_OK)
    
    
    def put(self, request):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        expense_id = request.query_params.get('expense_id', None)

        if expense_id is None :
            return Response({'error': 'Expense ID are required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not expense_id.isdigit():
            return Response({'error':  f" 'id' expected a number but got {expense_id}"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            expense_entry = ExtraExpensesHistory.objects.get(id=expense_id)
        except ExtraExpensesHistory.DoesNotExist:
            return Response({'error': 'Expense entry not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AllExtraExpenseSerializer(expense_entry, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Successfully Edited Expense.','data':serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        # IsAdminUser applited
        # self.permission_classes = [IsAdminUser]
        self.renderer_classes = [UserRenderer]
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        

        expense_id = request.query_params.get('expense_id', None)

        if expense_id is None :
            return Response({'error': 'Expense ID are required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not expense_id.isdigit():
            return Response({'error':  f" 'id' expected a number but got {expense_id}"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            expense_entry = ExtraExpensesHistory.objects.get(id=expense_id)
        except ExtraExpensesHistory.DoesNotExist:
            return Response({'error': 'Expense entry not found.'}, status=status.HTTP_404_NOT_FOUND)
            

        expense_entry.delete()
        return Response({'msg': f'{expense_entry.expense_name} -Deleted from your system'},status=status.HTTP_204_NO_CONTENT)
    

class PaymentEntryView(APIView):
    renderer_classes = [UserRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    def post(self, request):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        try:
            # Get the phone number from the request data
            phone_no = request.data['phone_no']
            submitted_amount=request.data['amount']
            get_date = request.data['date']

            # date convertin date format
            get_date = datetime.strptime(get_date, '%Y-%m-%d').date()

            today = date.today()
            if get_date > today:
                return Response({"error": "Date cannot be greater than today"}, status=status.HTTP_400_BAD_REQUEST)

            # Get the user ID using the phone number
            user = CustomUser.objects.get(phone_no=phone_no)
            user_id = user.id
        except CustomUser.DoesNotExist:
            return Response({'error':{'message': f'User with phone number {phone_no} not found'}})
        except Exception as e:
            return Response({'error':{'message': f'An unexpected error occurred: {e}'}})
       
       
        # Create the payment instance
        payment_history_data = {
            'user': user_id,
            'date': get_date,
            'submitted_amount': submitted_amount,
            
        }
        serializer = PaymentEntrySerializer(data=payment_history_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a success response
        return Response({ 'success' : True,
                         'msg': 'Payment successful',
                         'data': serializer.data,
                         })
    

    
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
        current_year = dt_datetime.datetime.now().year
        current_month = dt_datetime.datetime.now().month
        if year < 1900 or year > current_year:
            return Response({'Year Must be valid Or not greater than current year.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if month is within a valid range (1 to 12)
        if month < 1 or month > 12 or (current_year == year and current_month < month): 
            return Response({'error': 'Month Must have Valid Month or must request less that current month'}, status=status.HTTP_400_BAD_REQUEST)


        # Filter Extra Expenses entries for the specific, year, and month
        extra_expense_entries = UserPaymentHistory.objects.filter(
            date__year=year,
            date__month=month
        )

        extra_expenses_serializer = PaymentEntrySerializer(extra_expense_entries, many=True)

        return Response({'Success':True,'data':extra_expenses_serializer.data},status=status.HTTP_200_OK)
    
    def put(self, request):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        pay_id = request.query_params.get('pay_id', None)
        phone_no = request.data.get('phone_no', None)
        get_date_str = request.data.get('date', None)
        

        if pay_id is None :
            return Response({'error': 'Payment ID are required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not pay_id.isdigit():
            return Response({'error':  f" 'id' expected a number but got {pay_id}"}, status=status.HTTP_400_BAD_REQUEST)
        
        # date convertin date format
        if get_date_str:
            get_date = datetime.strptime(get_date_str, '%Y-%m-%d').date()

            today = date.today()
            if get_date > today:
                return Response({"error": "Date cannot be greater than today"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            payment_entry = UserPaymentHistory.objects.get(id=pay_id)
            if phone_no:
                
                user = CustomUser.objects.get(phone_no=phone_no, is_active=True)
                user_id = user.id
                # request.data['user'] = user_id
                 # Convert to mutable QueryDict
                mutable_data = request.data.copy()

                # Iterate through keys in request.data and update the mutable copy
                for key in request.data:
                    mutable_data[key] = request.data[key]

                # Add or update specific fields
                mutable_data['user'] = user_id

                # Use the mutable_data in the serializer
                serializer = PaymentEntrySerializer(payment_entry, data=mutable_data, partial=True)
            else:
                serializer = PaymentEntrySerializer(payment_entry, data=request.data, partial=True)

        except UserPaymentHistory.DoesNotExist:
            return Response({'error': 'Payment entry not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found. May be not active user'}, status=status.HTTP_404_NOT_FOUND)

        

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True,
                             'msg': 'Successfully Edited Payment.',
                             'data':serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request):
        # IsAdminUser applited
        self.permission_classes = [IsAdminUser]
        self.renderer_classes = [UserRenderer]
        self.check_permissions(request)

        pay_id = request.query_params.get('pay_id', None)

        if pay_id is None :
            return Response({'error': 'Payment ID are required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not pay_id.isdigit():
            return Response({'error':  f" 'id' expected a number but got {pay_id}"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            Payment_entry = UserPaymentHistory.objects.get(id=pay_id)
        except UserPaymentHistory.DoesNotExist:
            return Response({'error': 'Payment entry not found.'}, status=status.HTTP_404_NOT_FOUND)
            

        Payment_entry.delete()
        return Response({'msg': f'{Payment_entry.submitted_amount} amount is Deleted on {Payment_entry.date} from your system'},status=status.HTTP_204_NO_CONTENT)
    
    
class AvailabilityCheckView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    def post(self, request, *args, **kwargs):
        # Set default values for month, year, and is_available
        current_date = datetime.now()
        month = current_date.month
        year = current_date.year
        is_available = True

        # Get all active users
        active_users = CustomUser.objects.filter(is_active=True, is_superuser=False)

        # Save availability information for each user
        for user in active_users:
            existing_entry = UserAvailabilityCheck.objects.filter(user=user, month=month, year=year).first()

            if not existing_entry:
                # Create a new entry if none exists
                availability_check = UserAvailabilityCheck(
                    user=user,
                    month=month,
                    year=year,
                    is_available=is_available
                )
                availability_check.save()

        return Response({'message': 'Availability saved successfully'}, status=status.HTTP_200_OK)

    

