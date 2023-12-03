from django.shortcuts import render

from rest_framework.views import APIView
from InventoryApp.serializer import ItemSerializer,ItemSerializer
from account.renderers import UserRenderer
from rest_framework.response import Response
from .models import Item
# Create your views here.

class ItemCreateView(APIView):
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
        