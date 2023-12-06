from django.shortcuts import render

from rest_framework.views import APIView
from InventoryApp.serializer import ItemSerializer,ItemSerializer,InventorySerializer,InventoryDamageSerializer,SingleInventorySerializer
from account.renderers import UserRenderer
from rest_framework.response import Response
from rest_framework import status
from .models import Item,ItemInventory,UsageInventory
from django.db.models import ProtectedError
from datetime import datetime as dt
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import get_object_or_404
# Create your views here.

class ItemView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = ItemSerializer(data=request.data)
        # print(serializer.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': True,
                          'data': serializer.data})
    def get(self, request, format=None):
        item_id = request.query_params.get('item_id')

        if item_id:
            # If item_id is provided, get the specific item
            try:
                item = Item.objects.get(pk=item_id)
                serializer = ItemSerializer(item)
                return Response({'status': True, 'data': serializer.data})
            except Item.DoesNotExist:
                return Response({'status': False, 'error': f"Item with id {item_id} does not exist."}, status=404)
        else:
            # If item_id is not provided, get all items
            items = Item.objects.all()
            serializer = ItemSerializer(items, many=True)
            return Response({'status': True, 'data': serializer.data})
    
    def put(self, request, format=None):
        item_id = request.query_params.get('item_id', None)
        # user_id = request.query_params.get('user', None)

        if item_id is None : #or user_id is None
            return Response({'error': 'item id required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not item_id.isdigit() : #or not user_id.isdigit()
            return Response({'error':  " 'id' expected a number but got other"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            item_entry = Item.objects.get(id=item_id)
            # user = CustomUser.objects.get(id=user_id, is_active=True)
        except Item.DoesNotExist:
            return Response({'error': 'Item entry not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ItemSerializer(item_entry,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True,
                             'msg': 'Successfully Edited Bazar.',
                             'data':serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, format=None):

        item_id = request.query_params.get('item_id', None)
        # user_id = request.query_params.get('user', None)

        if item_id is None : #or user_id is None
            return Response({'error': 'item id required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not item_id.isdigit() : #or not user_id.isdigit()
            return Response({'error':  " 'id' expected a number but got other"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            item_entry = Item.objects.get(id=item_id)
            # user = CustomUser.objects.get(id=user_id, is_active=True)
        except Item.DoesNotExist:
            return Response({'error': 'Item entry not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
        try:
           item_entry.delete()
        except ProtectedError as e:
            return Response({
                 'success': False,
                'msg': f'This {item_entry.item_name} cannot be deleted because they have data in other DB.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            'success': True,
            'msg': f'{item_entry.item_name}-{item_entry.variant} -Deleted from your system'},status=status.HTTP_204_NO_CONTENT)

class SingleInventoryView(APIView):
    def get(self, request, format=None):
        # ItemSerializer
        inventory_id = request.query_params.get('inventory_id', None)
        # user_id = request.query_params.get('user', None)

        if inventory_id is None : #or user_id is None
            return Response({'error': 'inventory id required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not inventory_id.isdigit() : #or not user_id.isdigit()
            return Response({'error':  " 'id' expected a number but got other"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            item_inventory_entry = ItemInventory.objects.get(id=inventory_id)
            # user = CustomUser.objects.get(id=user_id, is_active=True)
        except ItemInventory.DoesNotExist:
            return Response({'error': 'Item entry not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SingleInventorySerializer(item_inventory_entry)
        return Response({'status': True, 'data': serializer.data})
        
        

class ItemInventoryView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = InventorySerializer(data=request.data)
        # print(serializer.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': True,
                          'data': serializer.data})
    def get(self, request, format=None):
        # Get query parameters from the request
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        item_id = request.query_params.get('item') 

        # Validate and parse month and year
        try:
            if month:
                month = int(month)
                if not year:
                    raise ValueError("Year is required when month is provided.")
            if year:
                year = int(year)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

        # Initialize filters
        filters = {}

        # Add month filter if provided
        if month:
            start_date = dt(year, month, 1)
            end_date = dt(year, month + 1, 1) if month < 12 else dt(year + 1, 1, 1)
            filters['purchase_date__gte'] = start_date
            filters['purchase_date__lt'] = end_date

        # Add year filter if provided
        if year:
            filters['purchase_date__year'] = year
        
        # Add item filter if provided
        if item_id:
            filters['item'] = item_id

        # Filter ItemInventory data based on the provided filters
        filtered_data = filtered_data = ItemInventory.objects.select_related('item').filter(**filters)

        # Serialize the filtered data
        serializer = InventorySerializer(filtered_data, many=True)
        return Response(serializer.data)
     
    def put(self, request, format=None):
        inventory_id = request.query_params.get('inventory_id', None)
        # user_id = request.query_params.get('user', None)

        if inventory_id is None : #or user_id is None
            return Response({'error': 'inventory id required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not inventory_id.isdigit() : #or not user_id.isdigit()
            return Response({'error':  " 'id' expected a number but got other"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            item_inventory_entry = ItemInventory.objects.get(id=inventory_id)
            # user = CustomUser.objects.get(id=user_id, is_active=True)
        except ItemInventory.DoesNotExist:
            return Response({'error': 'Item entry not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = InventorySerializer(item_inventory_entry,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True,
                             'msg': 'Successfully Edited Inventory.',
                             'data':serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, format=None):
        inventory_id = request.query_params.get('inventory_id', None)
        # user_id = request.query_params.get('user', None)

        if inventory_id is None : #or user_id is None
            return Response({'error': 'item id required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not inventory_id.isdigit() : #or not user_id.isdigit()
            return Response({'error':  " 'id' expected a number but got other"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            item_entry = ItemInventory.objects.get(id=inventory_id)
            # user = CustomUser.objects.get(id=user_id, is_active=True)
        except ItemInventory.DoesNotExist:
            return Response({'error': 'Item entry not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
        try:
           item_entry.delete()
        except ProtectedError as e:
            return Response({
                 'success': False,
                'msg': f'This {item_entry.id} cannot be deleted because they have data in other DB.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            'success': True,
            'msg': f'{item_entry.id} -Deleted from your system'},status=status.HTTP_204_NO_CONTENT)
    
class DamageAdd(APIView):
    def put(self, request, format=None):
        inventory_id = request.query_params.get('inventory_id', None)

        if inventory_id is None : #or user_id is None
            return Response({'error': 'inventory id required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not inventory_id.isdigit() : #or not user_id.isdigit()
            return Response({'error':  " 'id' expected a number but got other"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            item_inventory_entry = ItemInventory.objects.get(id=inventory_id)
            # user = CustomUser.objects.get(id=user_id, is_active=True)
        except ItemInventory.DoesNotExist:
            return Response({'error': 'Inventory Item entry not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
        # Assuming request.data contains 'damage_quantity' key with the new damage value
        new_damage_quantity_str = request.data.get('damage_quantity', '0')

        # Convert new_damage_quantity to Decimal
        new_damage_quantity = Decimal(new_damage_quantity_str)

        # Convert request.data to a mutable dictionary
        mutable_data = request.data.copy()

        # Add the new damage to the existing damage_quantity in the mutable dictionary
        mutable_data['damage_quantity'] = item_inventory_entry.damage_quantity + new_damage_quantity

        serializer = InventoryDamageSerializer(item_inventory_entry, data=mutable_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True,
                             'msg': 'Successfully Edited Inventory.',
                             'data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'success': False,
                             'msg': 'Damage Issued Failure',
                             'Error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class GetItemVariant(APIView):
    def get(self, request):
        item_name = request.query_params.get('item_name', None)

        if not item_name:
            return Response({'error': 'Item name is required'}, status=status.HTTP_400_BAD_REQUEST)

        items = Item.objects.filter(item_name=item_name)
        if not items:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class GetUniqueItemNames(APIView):
    def get(self, request):
        unique_item_names = Item.objects.values_list('item_name', flat=True).distinct()
        return Response({'unique_item_names': list(unique_item_names)}, status=status.HTTP_200_OK)
    
class StockView(APIView):
    def get(self, request):
        try:
            item_id = request.query_params.get('item_id', None)
            
            if item_id is None : #or user_id is None
                return Response({'error': 'item id required in the request Params.'}, status=status.HTTP_400_BAD_REQUEST)
        
            if not item_id.isdigit() : #or not user_id.isdigit()
                return Response({'error':  " 'id' expected a number but got other"}, status=status.HTTP_400_BAD_REQUEST)

            item_inventory = ItemInventory.objects.filter(item=item_id)
            total_quantity = item_inventory.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
            total_damage_quantity = item_inventory.aggregate(total_damage_quantity=Sum('damage_quantity'))['total_damage_quantity'] or 0
            purchase_count = item_inventory.count()

           

            item_usages = UsageInventory.objects.filter(item=item_id)
            total_usages = item_usages.aggregate(usages=Sum('quantity_used'))['usages'] or 0

            result={
                'purchase_count': purchase_count,
                'total_purchases_quantity':total_quantity,
                'total_usages': total_usages,
                'total_damage_quantity': total_damage_quantity,
                'inventory_stock': total_quantity-total_usages-total_damage_quantity,

            }


            return Response({
                'success': True,
                'data': result
            }, status=status.HTTP_200_OK)
        except ItemInventory.DoesNotExist:
            return Response({
                'success': False,
                'error': 'ItemInventory not found'}, status=status.HTTP_404_NOT_FOUND)
    
         