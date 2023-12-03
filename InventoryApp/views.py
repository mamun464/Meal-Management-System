from django.shortcuts import render

from rest_framework.views import APIView
from InventoryApp.serializer import ItemSerializer,ItemSerializer
from account.renderers import UserRenderer
from rest_framework.response import Response
from rest_framework import status
from .models import Item
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
        items= Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response({'status': True,
                          'data': serializer.data})
    
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
        
        item_entry.delete()
        return Response({
            'success': True,
            'msg': f'{item_entry.item_name}-{item_entry.variant} -Deleted from your system'},status=status.HTTP_204_NO_CONTENT)