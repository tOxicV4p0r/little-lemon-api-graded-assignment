from rest_framework import serializers
from rest_framework.validators import UniqueValidator,UniqueTogetherValidator
from decimal import Decimal
from django.contrib.auth.models import User 
from .models import Category, MenuItem, Cart, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','slug','title']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category']
        extra_kwargs = {
            'price': {'min_value': 1},
            'title':{
                'validators':[
                    UniqueValidator(queryset=MenuItem.objects.all())
                ]
            }
        }

class CartSerializer(serializers.ModelSerializer):
    def cal_price(self, product:Cart):
        return Decimal(product.quantity)* Decimal(product.unit_price)
    
    price = serializers.SerializerMethodField(method_name='cal_price')
    
    user = serializers.PrimaryKeyRelatedField( 
        queryset = User.objects.all(),
        default = serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Cart
        fields = ['id','user','menuitem','quantity','unit_price','price']

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField( 
        queryset = User.objects.all(),
        default = serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Order
        fields = ['id','user','delivery_crew','status','total','date']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id','order','menuitem','quantity','unit_price','price']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']