from django.shortcuts import render,get_object_or_404
from django.db import IntegrityError
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.decorators import permission_required

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.views import APIView

from .permissions import IsManagerPostOrReadOnly, IsManagerEditOrReadOnly
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, DjangoModelPermissionsOrAnonReadOnly
from rest_framework.decorators import permission_classes, throttle_classes
from django.contrib.auth.models import User, Group

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from rest_framework import generics
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer

# Create your views here.
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    permission_classes = [IsManagerPostOrReadOnly]
    # throttle_classes = [AnonRateThrottle,UserRateThrottle]
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer

class SingleMenuItemView(generics.RetrieveUpdateAPIView,generics.DestroyAPIView):
    permission_classes = [IsManagerEditOrReadOnly]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


""" 
@api_view(['GET','POST','PUT','PATCH','DELETE'])
def menu_items(req):
    if req.method =='GET':
        items = MenuItem.objects.select_related('category').all()
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data, status.HTTP_200_OK)
    
    if req.user.groups.filter(name='Manager').exists():
        if( req.method == 'POST'):
            serialized_item = MenuItemSerializer(data = req.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status.HTTP_201_CREATED)

    return Response({"message":"You are not authorized"}, status.HTTP_403_FORBIDDEN)

@api_view(['GET','PUT','PATCH','DELETE'])
def menu_items_detail(req, pk):
    if req.method =='GET':
        items = get_object_or_404(MenuItem,pk=pk)
        serialized_item = MenuItemSerializer(items)
        return Response(serialized_item.data, status.HTTP_200_OK) 
    
    if req.user.groups.filter(name='Manager').exists():
        if( req.method == 'PUT' or req.method == 'PATCH'):
            serialized_item = MenuItemSerializer(data = req.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status.HTTP_200_OK)
    
    return Response({"message":"You are not authorized"}, status.HTTP_403_FORBIDDEN) 

"""