import requests
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status

def CallMonthlyTotalMealAPI(year, month):
    try:
        # Define the URL of your API endpoint
        base_url = "http://127.0.0.1:8000"  # Your base URL
        api_url = f"{base_url}/api/hostel/all-meal-monthly/"

        # Define the JSON data to send in the request body
        json_data = {
            "year": year,
            "month": month,
        }

        # Make a POST request to the API
        response = requests.post(api_url, json=json_data)

        if response.status_code == 200:
            # Successful API call
            api_data = response.json()
            return {'success': True, 'data': api_data}
        else:
            # Handle API call errors
            return {'success': False, 'error': f"API call error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        # Handle request-related errors (e.g., network issues)
        return {'success': False, 'error': f"Request error: {str(e)}"}
    except Exception as e:
        # Handle other unexpected errors
        return {'success': False, 'error': f"An unexpected error occurred: {str(e)}"}

