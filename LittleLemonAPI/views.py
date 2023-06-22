from django.shortcuts import get_object_or_404, get_list_or_404
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

from .permissions import IsManagerPostOrReadOnly, IsManagerEditOrReadOnly, IsManager
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, DjangoModelPermissionsOrAnonReadOnly
from rest_framework.decorators import permission_classes, throttle_classes
from django.contrib.auth.models import User, Group

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from rest_framework import generics
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer

# Create your views here.
class CategoriesView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle,UserRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    permission_classes = [IsManagerPostOrReadOnly,IsAuthenticated]
    throttle_classes = [AnonRateThrottle,UserRateThrottle]
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer

class SingleMenuItemView(generics.RetrieveUpdateAPIView,generics.DestroyAPIView):
    permission_classes = [IsManagerEditOrReadOnly,IsAuthenticated]
    throttle_classes = [AnonRateThrottle,UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle,UserRateThrottle]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)
    
    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        items = Cart.objects.filter(user=user)
        items.delete()
        return Response({"message":"deleted"},status.HTTP_204_NO_CONTENT)


class OrderView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle,UserRateThrottle]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        user = self.request.user
        items = get_list_or_404(Cart, user=user)
        # valid_objects = []
        orderId = 1
        for data in items:
            serializeObject = OrderItemSerializer(data=data)
            
            if serializeObject.is_valid():
                serializeObject.save()
            else:
                return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)
        # for obj in valid_objects:
        #   obj.save()

@api_view(['GET','POST'])
@permission_classes([IsAdminUser|IsManager])
@throttle_classes([AnonRateThrottle,UserRateThrottle])
def manager_list(req):
    if( req.method == 'GET'):
        users = User.objects.filter(groups__name='Manager')
        serialized_item = UserSerializer(users, many=True)
        return Response(serialized_item.data, status.HTTP_200_OK)
    
    
    if 'username' in req.data :
        username = req.data.get('username')
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if req.method =='POST':
            managers.user_set.add(user)
            return Response({"message":"added"}, status.HTTP_201_CREATED)
    
    else:
        return Response({"message": "Required field not found."}, status.HTTP_400_BAD_REQUEST)

    return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser|IsManager])
@throttle_classes([AnonRateThrottle,UserRateThrottle])
def manager_del(req,userId):
    get_object_or_404(User,groups__name='Manager',pk=userId) 
    user = get_object_or_404(User, id=userId)
    managers = Group.objects.get(name="Manager")
    
    if req.method == 'DELETE':
        managers.user_set.remove(user)
        return Response({"message":"deleted"}, status.HTTP_200_OK)

    return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
@permission_classes([IsAdminUser|IsManager])
@throttle_classes([AnonRateThrottle,UserRateThrottle])
def delivery_crew_list(req):
    if( req.method == 'GET'):
        users = User.objects.filter(groups__name='Delivery crew')
        serialized_item = UserSerializer(users, many=True)
        return Response(serialized_item.data, status.HTTP_200_OK)
    
    username = req.data.get('username')
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Delivery crew")
        if req.method =='POST':
            managers.user_set.add(user)
            return Response({"message":"added"}, status.HTTP_201_CREATED)

    return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser|IsManager])
@throttle_classes([AnonRateThrottle,UserRateThrottle])
def delivery_crew_del(req,userId):
    get_object_or_404(User,groups__name='Delivery crew',pk=userId) 
    user = get_object_or_404(User, id=userId)
    managers = Group.objects.get(name="Delivery crew")
    
    if req.method == 'DELETE':
        managers.user_set.remove(user)
        return Response({"message":"deleted"}, status.HTTP_200_OK)

    return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle,UserRateThrottle])
def order_list(req):
    user = req.user
    if( req.method == 'GET'):
        if( user.groups.filter(name="Manager").exists() ) :
            items = Order.objects.all()
            serialized_item = OrderSerializer(items,many=True)
            return Response(serialized_item.data, status.HTTP_200_OK)
        
        if( user.groups.filter(name="Delivery crew").exists() ) :
            items = Order.objects.filter(delivery_crew=user)
            serialized_item = OrderSerializer(items,many=True)
            return Response(serialized_item.data, status.HTTP_200_OK)
        
        # items = get_list_or_404(Order,user=user)
        items = Order.objects.filter(user=user)
        # items = Order.objects.select_related('user').all()
        serialized_item = OrderSerializer(items, many=True)
        return Response(serialized_item.data, status.HTTP_200_OK)
    
    if req.method =='POST':
        # if don't have item on Cart -> return 404 not found items
        items = get_list_or_404(Cart,user=user)

        # fix dummy data
        deliveryCrewId = 2
        state = False
        total = float("23.23")
        date = "2023-06-23"
        diliveryUser = get_object_or_404(User, pk=deliveryCrewId)

        order = Order(
            user = user,
            delivery_crew = diliveryUser,
            status = state,
            total = total,
            date = date
        )
        
        # save Order -> get orderId
        serialized_item = OrderSerializer(data = model_to_dict(order))
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()

        # get Orderitem from Cart
        orderId = serialized_item.data['id']
        orderInst = get_object_or_404(Order, id=serialized_item.data['id'])  
        serialized_item = CartSerializer(items, many=True)
        for item in serialized_item.data:
            menuitem = get_object_or_404(MenuItem, id=item['menuitem'])
            obj = OrderItem(
                order = orderInst,
                menuitem = menuitem,
                quantity = item['quantity'],
                unit_price = item['unit_price'],
                price = item['price'],
            )
            serialized_item = OrderItemSerializer(data = model_to_dict(obj))
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()

        # remove menuitem from Cart
        Cart.objects.filter(user=user).delete()

        return Response(serialized_item.data, status.HTTP_201_CREATED)
 
    return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle,UserRateThrottle])
def order_detail(req,orderId):
    user = req.user
    
    if( user.groups.filter(name="Manager").exists() ) :
        if( req.method == 'PUT'):
            if 'status' in req.data and 'delivery_crew' in req.data:
                deliveryCrewId = req.data.get('delivery_crew')
                diliveryUser = get_object_or_404(User, id=deliveryCrewId)
                state = bool(req.data.get('status'))
                item = get_object_or_404(Order,pk=orderId)
                item.delivery_crew = diliveryUser
                item.status = state
                OrderSerializer(item)
                item.save()
                serialized_item = OrderSerializer(item)
                return Response(serialized_item.data, status.HTTP_200_OK)
            else:
                return Response({"message": "Required field not found."}, status.HTTP_400_BAD_REQUEST)
        
        if( req.method == 'PATCH'):
            if 'status' in req.data:
                state = bool(req.data.get('status'))
                item = get_object_or_404(Order,pk=orderId)
                item.status = state
                item.save()
                serialized_item = OrderSerializer(item)
                return Response(serialized_item.data, status.HTTP_200_OK)
            else:
                return Response({"message": "Required field not found."}, status.HTTP_400_BAD_REQUEST)

        if req.method == 'DELETE':
            # delete order
            get_object_or_404(Order,pk=orderId).delete()
            return Response({"message":"deleted"}, status.HTTP_200_OK)
        
        return Response({"message":"Method not allowed"},status.HTTP_403_FORBIDDEN)
        
    if( user.groups.filter(name="Delivery crew").exists() ):
        if( req.method == 'PATCH'):
            if 'status' in req.data:
                state = bool(req.data.get('status'))
                item = get_object_or_404(Order,delivery_crew=user,pk=orderId)
                item.status = state
                item.save()
                serialized_item = OrderSerializer(item)
                return Response(serialized_item.data, status.HTTP_200_OK)
            else:
                return Response({"message": "Required field not found."}, status.HTTP_400_BAD_REQUEST)
                
        return Response({"message":"Method not allowed"},status.HTTP_403_FORBIDDEN)
        
    if( req.method == 'GET'):
        get_object_or_404(Order,user=user,pk=orderId)
        items = get_list_or_404(OrderItem,order=orderId)
        serialized_item = OrderItemSerializer(items,many=True)
        return Response(serialized_item.data, status.HTTP_200_OK)
    
    return Response({"message":"Method not allowed"},status.HTTP_403_FORBIDDEN)


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