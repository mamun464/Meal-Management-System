import requests
import pprint
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status

base_url = "http://127.0.0.1:8000"

def CallMonthlyTotalMealAPI(year, month):
    try:
        # Define the URL of your API endpoint
         # Your base URL
        api_url = f"{base_url}/api/hostel/all-meal-monthly/"

        # Define the JSON data to send in the request body
        params = {
            "year": year,
            "month": month,
        }

        # Make a POST request to the API
        response = requests.post(api_url, params=params)

        if response.status_code == 200:
            # Successful API call
            api_data = response.json()
            return {'success': True, 'data': api_data}
        else:
            # Handle API call errors
            return {'success': False, 'error': f"API call error(all-meal-monthly API): {response.status_code}",
                    
                    'msg': api_data
                    }
    except requests.exceptions.RequestException as e:
        # Handle request-related errors (e.g., network issues)
        return {'success': False, 'error': f"Request error (all-meal-monthly API): {str(e)}"}
    except Exception as e:
        # Handle other unexpected errors
        return {'success': False, 'error': f"An unexpected error occurred (all-meal-monthly API): {str(e)}"}
    

def CallMealRateAPI(year, month):
    try:
        # Define the URL of your API endpoint
         # Your base URL
        api_url = f"{base_url}/api/hostel/meal-rate/"

        # Define the JSON data to send in the request body
        params = {
            "year": year,
            "month": month,
        }

        # Make a POST request to the API
        response = requests.post(api_url, params=params)

        if response.status_code == 200:
            # Successful API call
            api_data = response.json()
            return {'success': True, 'data': api_data}
        else:
            # Handle API call errors
            return {'success': False, 'error': f"API call error (meal-rate API): {response.status_code}",
                    'msg': api_data
                    }
    except requests.exceptions.RequestException as e:
        # Handle request-related errors (e.g., network issues)
        return {'success': False, 'error': f"Request error (meal-rate API): {str(e)}"}
    except Exception as e:
        # Handle other unexpected errors
        return {'success': False, 'error': f"An unexpected error occurred (meal-rate API): {str(e)}"}
    

def CallBazarListAPI(year, month):
    try:
        # Define the URL of your API endpoint
         # Your base URL
        api_url = f"{base_url}/api/hostel/monthly-allbazar-list/"

        # Define the JSON data to send in the request body
        params = {
            "year": year,
            "month": month,
        }

        

        # Make a POST request to the API
        response = requests.get(api_url, params=params)
        print(response)

        if response.status_code == 200:
            # Successful API call
            api_data = response.json()
            return {'success': True, 'data': api_data}
        else:
            # Handle API call errors
            api_data = response.json()
            return {'success': False, 
                    'error': f"API call error (monthly-all-bazar-list API): {response.status_code}",
                    'msg': api_data
                    }
    except requests.exceptions.RequestException as e:
        # Handle request-related errors (e.g., network issues)
        return {'success': False, 'error': f"Request error (monthly-all-bazar-list API): {str(e)}"}
    except Exception as e:
        # Handle other unexpected errors
        return {'success': False, 'error': f"An unexpected error occurred (monthly-all-bazar-list API): {str(e)}"}
    

def CallMonthlySingleUserDetailsAPI(user_id,year, month):
    try:
        # Define the URL of your API endpoint
         # Your base URL
        api_url = f"{base_url}/api/hostel/monthly-all-user-details/"

        # Define the JSON data to send in the request body
        params = {
            "year": year,
            "month": month,
            "user":user_id,
        }

        

        # Make a POST request to the API
        response = requests.get(api_url, params=params)
        print(response)

        if response.status_code == 200:
            # Successful API call
            api_data = response.json()
            pprint(api_data)
            return {'success': True, 'data': api_data}
        else:
            # Handle API call errors
            api_data = response.json()
            return {'success': False, 
                    'error': f"API call error (monthly-all-user-details): {response.status_code}",
                    'msg': api_data
                    }
    except requests.exceptions.RequestException as e:
        # Handle request-related errors (e.g., network issues)
        return {'success': False, 'error': f"Request error (monthly-all-user-details): {str(e)}"}
    except Exception as e:
        # Handle other unexpected errors
        return {'success': False, 'error': f"An unexpected error occurred (monthly-all-user-details): {str(e)}"}


def CallExtraCostAPI(year, month):
    try:
        # Define the URL of your API endpoint
         # Your base URL
        api_url = f"{base_url}/api/hostel/monthly-extra-expense-list/"

        # Define the JSON data to send in the request body
        params = {
            "year": year,
            "month": month,
        }

        # Make a POST request to the API
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
           
            # Successful API call
            api_data = response.json()
            return {'success': True, 'data': api_data}
        else:
            # Handle API call errors
            api_data = response.json()
            return {'success': False, 
                    'error': f"API call error-1 (monthly-extra-expense-list): {response.status_code}",
                    'msg': api_data
                    }
    except requests.exceptions.RequestException as e:
        # Handle request-related errors (e.g., network issues)
        return {'success': False, 'error': f"Request error-2 (monthly-extra-expense-list): {str(e)}"}
    except Exception as e:
        # Handle other unexpected errors
        return {'success': False, 'error': f"An unexpected error occurred-3 (monthly-extra-expense-list): {str(e)}"}
    


def CallPaymentListAPI(year, month):
    try:
        # Define the URL of your API endpoint
         # Your base URL
        api_url = f"{base_url}/api/hostel/monthly-payment-data/"

        # Define the JSON data to send in the request body
        params = {
            "year": year,
            "month": month,
        }

        # Make a POST request to the API
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
           
            # Successful API call
            api_data = response.json()
            return {'data': api_data}
        else:
            # Handle API call errors
            api_data = response.json()
            return {'success': False, 
                    'error': f"API call error-1 (CallPaymentListAPI): {response.status_code}",
                    'msg': api_data
                    }
    except requests.exceptions.RequestException as e:
        # Handle request-related errors (e.g., network issues)
        return {'success': False, 'error': f"Request error-2 (CallPaymentListAPI): {str(e)}"}
    except Exception as e:
        # Handle other unexpected errors
        return {'success': False, 'error': f"An unexpected error occurred-3 (CallPaymentListAPI): {str(e)}"}
